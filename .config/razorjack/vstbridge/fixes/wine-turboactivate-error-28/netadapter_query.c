/* Runs the two MSFT_NetAdapter queries that TurboActivate issues and prints the
 * rows. Addresses are masked unless --full is given, so the output can be pasted.
 *
 * x86_64-w64-mingw32-gcc -municode -o netadapter_query.exe netadapter_query.c \
 *     -lole32 -loleaut32 -lwbemuuid
 *
 * Exit status: 0 when the strict query returns a row with a PermanentAddress,
 * 1 when it does not, 2 when a WMI call fails.
 */
#define COBJMACROS
#include <stdio.h>
#include <wchar.h>
#include <windows.h>
#include <wbemcli.h>

#define Q_COMMON L"SELECT DeviceID, PermanentAddress, PNPDeviceID, WdmInterface FROM MSFT_NetAdapter WHERE "
#define Q_TAIL L"(InterfaceType = 6 OR InterfaceType = 71) AND NOT NdisPhysicalMedium = 10 AND NOT PNPDeviceID LIKE \"ROOT\\\\%\""

static const WCHAR strict_query[] = Q_COMMON
    L"(Virtual = FALSE AND NOT PNPDeviceID LIKE \"XEN%\\\\%\" AND NOT PNPDeviceID LIKE \"VMBUS\\\\%\") AND " Q_TAIL;
static const WCHAR relaxed_query[] = Q_COMMON Q_TAIL;

static void print_bstr( const WCHAR *label, IWbemClassObject *row, const WCHAR *name, BOOL mask )
{
    VARIANT value;

    VariantInit( &value );
    if (FAILED( IWbemClassObject_Get( row, name, 0, &value, NULL, NULL ) ))
        wprintf( L"  %ls: <error>\n", label );
    else if (V_VT( &value ) != VT_BSTR)
        wprintf( L"  %ls: <null>\n", label );
    else if (mask && SysStringLen( V_BSTR( &value ) ) >= 6)
        wprintf( L"  %ls: %.6ls******\n", label, V_BSTR( &value ) );
    else
        wprintf( L"  %ls: %ls\n", label, V_BSTR( &value ) );
    VariantClear( &value );
}

static HRESULT run_query( IWbemServices *services, const WCHAR *query, BOOL full, UINT *rows, UINT *with_address )
{
    IEnumWbemClassObject *result;
    IWbemClassObject *row;
    VARIANT value;
    ULONG count;
    BSTR language, text;
    HRESULT hr;

    *rows = *with_address = 0;
    language = SysAllocString( L"WQL" );
    text = SysAllocString( query );
    hr = IWbemServices_ExecQuery( services, language, text, WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY,
                                  NULL, &result );
    SysFreeString( language );
    SysFreeString( text );
    if (FAILED( hr )) return hr;

    while (IEnumWbemClassObject_Next( result, WBEM_INFINITE, 1, &row, &count ) == S_OK && count)
    {
        wprintf( L"row %u\n", *rows );
        print_bstr( L"DeviceID", row, L"DeviceID", FALSE );
        print_bstr( L"PermanentAddress", row, L"PermanentAddress", !full );
        print_bstr( L"PNPDeviceID", row, L"PNPDeviceID", FALSE );
        VariantInit( &value );
        if (SUCCEEDED( IWbemClassObject_Get( row, L"WdmInterface", 0, &value, NULL, NULL ) ))
            wprintf( L"  WdmInterface: %ls\n", V_BOOL( &value ) ? L"TRUE" : L"FALSE" );
        VariantClear( &value );
        VariantInit( &value );
        if (SUCCEEDED( IWbemClassObject_Get( row, L"PermanentAddress", 0, &value, NULL, NULL ) ) &&
            V_VT( &value ) == VT_BSTR && SysStringLen( V_BSTR( &value ) ))
            (*with_address)++;
        VariantClear( &value );
        IWbemClassObject_Release( row );
        (*rows)++;
    }
    IEnumWbemClassObject_Release( result );
    return S_OK;
}

int wmain( int argc, WCHAR *argv[] )
{
    IWbemLocator *locator;
    IWbemServices *services;
    BSTR path;
    HRESULT hr;
    UINT strict_rows, strict_addresses, relaxed_rows, relaxed_addresses;
    BOOL full = argc > 1 && !wcscmp( argv[1], L"--full" );

    hr = CoInitializeEx( NULL, COINIT_MULTITHREADED );
    if (SUCCEEDED( hr ))
        hr = CoCreateInstance( &CLSID_WbemLocator, NULL, CLSCTX_INPROC_SERVER, &IID_IWbemLocator, (void **)&locator );
    if (FAILED( hr ))
    {
        wprintf( L"cannot create the WMI locator: 0x%08lx\n", hr );
        return 2;
    }
    path = SysAllocString( L"ROOT\\StandardCimv2" );
    hr = IWbemLocator_ConnectServer( locator, path, NULL, NULL, NULL, 0, NULL, NULL, &services );
    SysFreeString( path );
    if (FAILED( hr ))
    {
        wprintf( L"cannot connect to root\\StandardCimv2: 0x%08lx\n", hr );
        return 2;
    }

    wprintf( L"strict query\n" );
    hr = run_query( services, strict_query, full, &strict_rows, &strict_addresses );
    if (FAILED( hr ))
    {
        wprintf( L"strict query failed: 0x%08lx\n", hr );
        return 2;
    }
    wprintf( L"relaxed query\n" );
    hr = run_query( services, relaxed_query, full, &relaxed_rows, &relaxed_addresses );
    if (FAILED( hr ))
    {
        wprintf( L"relaxed query failed: 0x%08lx\n", hr );
        return 2;
    }
    wprintf( L"strict: %u rows, %u with an address; relaxed: %u rows, %u with an address\n",
             strict_rows, strict_addresses, relaxed_rows, relaxed_addresses );

    IWbemServices_Release( services );
    IWbemLocator_Release( locator );
    CoUninitialize();
    return strict_addresses ? 0 : 1;
}
