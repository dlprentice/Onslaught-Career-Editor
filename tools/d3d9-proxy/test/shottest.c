/* bea-d3d9-proxy -- back-buffer grab self-test host.
 *
 * Drives the proxy's Present-time grab through a REAL device that really
 * rasterises, so the grab has something known to read. The window is created
 * off-screen and is NEVER shown: nothing appears, and no focus is taken.
 *
 * Each frame is cleared to an exact colour and presented. Two of the four
 * colours are the measured retail screen signatures this instrument exists to
 * reproduce, so a wrong channel order or a wrong PNG encoding shows up as a
 * wrong number rather than as a picture someone has to look at.
 */

#define WIN32_LEAN_AND_MEAN
#define CINTERFACE
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>

typedef IDirect3D9 *(WINAPI *PFN_Create9)(UINT);

/* frame -> clear colour. Frames 0/1 are the measured main-menu client mean and
 * 2/3 the measured click-to-start mean; the repeats exist so `change` mode has
 * something that must NOT be written. */
static const struct { int r, g, b; } frames[4] = {
    { 35, 37, 60 },
    { 35, 37, 60 },
    { 73, 79, 94 },
    { 73, 79, 94 },
};

int main(void)
{
    HMODULE mod;
    PFN_Create9 create;
    IDirect3D9 *d3d;
    IDirect3DDevice9 *dev = NULL;
    D3DPRESENT_PARAMETERS pp;
    WNDCLASSA wc;
    HWND wnd;
    HRESULT hr;
    char path[MAX_PATH];
    int i;

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = DefWindowProcA;
    wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = "beaShotTest";
    RegisterClassA(&wc);
    /* Off-screen and never shown. */
    wnd = CreateWindowExA(0, "beaShotTest", "bea shot self-test", WS_POPUP,
                          -20000, -20000, 64, 48, NULL, NULL, wc.hInstance, NULL);
    if (!wnd) {
        printf("FAIL: CreateWindow\n");
        return 2;
    }

    mod = LoadLibraryA("d3d9.dll");
    if (!mod) {
        printf("FAIL: LoadLibrary d3d9.dll\n");
        return 2;
    }
    path[0] = 0;
    GetModuleFileNameA(mod, path, MAX_PATH);
    printf("d3d9.dll = %s\n", path);

    create = (PFN_Create9)GetProcAddress(mod, "Direct3DCreate9");
    if (!create) {
        printf("FAIL: no Direct3DCreate9\n");
        return 2;
    }
    d3d = create(D3D_SDK_VERSION);
    if (!d3d) {
        printf("FAIL: Direct3DCreate9 returned NULL\n");
        return 2;
    }

    memset(&pp, 0, sizeof(pp));
    pp.BackBufferWidth = 64;
    pp.BackBufferHeight = 48;
    pp.BackBufferFormat = D3DFMT_X8R8G8B8;
    pp.BackBufferCount = 1;
    pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
    pp.hDeviceWindow = wnd;
    pp.Windowed = TRUE;
    pp.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;

    hr = d3d->lpVtbl->CreateDevice(d3d, D3DADAPTER_DEFAULT, D3DDEVTYPE_HAL, wnd,
                                   D3DCREATE_SOFTWARE_VERTEXPROCESSING, &pp,
                                   &dev);
    if (FAILED(hr) || !dev) {
        /* Desktop is not 32bpp, or no HAL: let the runtime pick the format. */
        pp.BackBufferFormat = D3DFMT_UNKNOWN;
        hr = d3d->lpVtbl->CreateDevice(d3d, D3DADAPTER_DEFAULT, D3DDEVTYPE_HAL,
                                       wnd, D3DCREATE_SOFTWARE_VERTEXPROCESSING,
                                       &pp, &dev);
    }
    if (FAILED(hr) || !dev) {
        printf("FAIL: CreateDevice -> 0x%08lX\n", (unsigned long)hr);
        return 2;
    }

    for (i = 0; i < 4; ++i) {
        dev->lpVtbl->Clear(dev, 0, NULL, D3DCLEAR_TARGET,
                           D3DCOLOR_XRGB(frames[i].r, frames[i].g, frames[i].b),
                           1.0f, 0);
        dev->lpVtbl->BeginScene(dev);
        dev->lpVtbl->EndScene(dev);
        dev->lpVtbl->Present(dev, NULL, NULL, NULL, NULL);
        printf("frame %d cleared to %d,%d,%d\n", i, frames[i].r, frames[i].g,
               frames[i].b);
    }

    dev->lpVtbl->Release(dev);
    d3d->lpVtbl->Release(d3d);
    DestroyWindow(wnd);
    printf("done\n");
    return 0;
}
