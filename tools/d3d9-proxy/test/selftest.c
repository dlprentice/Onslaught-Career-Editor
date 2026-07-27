/* bea-d3d9-proxy self-test.
 *
 * A 32-bit host that drives the proxy through the exact chain the game will:
 * Direct3DCreate9 -> CreateDevice -> Clear/BeginScene/draws/EndScene/Present.
 * It resolves d3d9.dll by bare name from its own directory, so the proxy is
 * loaded by the same search-order rule that will pick it up next to BEA.exe.
 *
 * The device is D3DDEVTYPE_NULLREF and the window is created without
 * WS_VISIBLE and never shown, so running this displays nothing and steals no
 * focus.
 *
 * Draws are chosen to cover both vertex paths and known screen coordinates:
 *   draw 0  DrawPrimitiveUP, XYZRHW|DIFFUSE|TEX1 quad at (100,50)-(228,146)
 *   draw 1  DrawPrimitive from a readable vertex buffer, same layout at
 *           (300,200)-(428,296)
 *   draw 2  DrawPrimitive from a D3DUSAGE_WRITEONLY buffer, which must be
 *           reported as unreadable rather than locked
 *
 * Frames 0..2 run those three. Frame 3 is a forensics frame that drives the
 * paths where the instrument must REFUSE rather than print a number:
 *   draw 0  a draw with more vertices than BEA_D3D9_MAXVERTS
 *   draw 1  a bound vertex buffer released while still bound, with a fresh
 *           buffer allocated straight afterwards so the allocator gets every
 *           chance to hand the same heap block back
 *   draw 2  a draw spanning the GAP between two disjoint locked ranges
 *   draw 3  a Lock(0, 0, D3DLOCK_DISCARD) ring buffer -- the idiom whose
 *           written extent cannot be known
 *   draw 4  a control draw, to prove none of the above poisoned the instrument
 */

#define WIN32_LEAN_AND_MEAN
#define CINTERFACE
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>

typedef IDirect3D9 *(WINAPI *PFN_Create9)(UINT);

typedef struct {
    float x, y, z, rhw;
    DWORD colour;
    float u, v;
} Vtx;

#define VFVF (D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1)

static void fill_quad(Vtx *v, float x0, float y0, float x1, float y1, DWORD c)
{
    v[0].x = x0; v[0].y = y0; v[1].x = x1; v[1].y = y0;
    v[2].x = x1; v[2].y = y1; v[3].x = x0; v[3].y = y1;
    {
        int i;
        for (i = 0; i < 4; ++i) {
            v[i].z = 0.0f;
            v[i].rhw = 1.0f;
            v[i].colour = c;
            v[i].u = (i == 1 || i == 2) ? 1.0f : 0.0f;
            v[i].v = (i >= 2) ? 1.0f : 0.0f;
        }
    }
}

int main(void)
{
    HMODULE d3d9;
    PFN_Create9 create;
    IDirect3D9 *d3d;
    IDirect3DDevice9 *dev = NULL;
    IDirect3DVertexBuffer9 *vbRead = NULL, *vbWrite = NULL;
    D3DPRESENT_PARAMETERS pp;
    WNDCLASSW wc;
    HWND hwnd;
    HRESULT hr;
    Vtx quad[4];
    void *p;
    int frame;

    d3d9 = LoadLibraryW(L"d3d9.dll");
    if (!d3d9) {
        printf("FAIL: LoadLibrary(d3d9.dll) -> %lu\n", GetLastError());
        return 2;
    }
    {
        wchar_t path[MAX_PATH] = {0};
        GetModuleFileNameW(d3d9, path, MAX_PATH);
        printf("loaded d3d9: %ls\n", path);
    }
    create = (PFN_Create9)GetProcAddress(d3d9, "Direct3DCreate9");
    if (!create) {
        printf("FAIL: no Direct3DCreate9 export\n");
        return 2;
    }
    /* Prove the ordinal-only forwards resolve too -- a missing one is a crash
     * at load for anything that imports by ordinal. */
    {
        int ord;
        for (ord = 16; ord <= 38; ++ord) {
            if (!GetProcAddress(d3d9, MAKEINTRESOURCEA(ord))) {
                printf("FAIL: ordinal %d does not resolve\n", ord);
                return 2;
            }
        }
        printf("all ordinals 16..38 resolve\n");
    }

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = DefWindowProcW;
    wc.hInstance = GetModuleHandleW(NULL);
    wc.lpszClassName = L"BeaD3D9SelfTest";
    RegisterClassW(&wc);
    /* No WS_VISIBLE, never shown: nothing appears on screen. */
    hwnd = CreateWindowExW(0, L"BeaD3D9SelfTest", L"", WS_POPUP, 0, 0, 640, 480,
                           NULL, NULL, wc.hInstance, NULL);
    if (!hwnd) {
        printf("FAIL: CreateWindowEx -> %lu\n", GetLastError());
        return 2;
    }

    d3d = create(D3D_SDK_VERSION);
    if (!d3d) {
        printf("FAIL: Direct3DCreate9 returned NULL\n");
        return 2;
    }
    printf("IDirect3D9 = %p\n", (void *)d3d);

    memset(&pp, 0, sizeof(pp));
    pp.BackBufferWidth = 640;
    pp.BackBufferHeight = 480;
    pp.BackBufferFormat = D3DFMT_X8R8G8B8;
    pp.BackBufferCount = 1;
    pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
    pp.hDeviceWindow = hwnd;
    pp.Windowed = TRUE;
    pp.EnableAutoDepthStencil = TRUE;
    pp.AutoDepthStencilFormat = D3DFMT_D16;

    hr = d3d->lpVtbl->CreateDevice(d3d, D3DADAPTER_DEFAULT, D3DDEVTYPE_NULLREF,
                                   hwnd, D3DCREATE_SOFTWARE_VERTEXPROCESSING,
                                   &pp, &dev);
    if (FAILED(hr) || !dev) {
        printf("FAIL: CreateDevice -> 0x%08lX\n", (unsigned long)hr);
        return 2;
    }
    printf("IDirect3DDevice9 = %p\n", (void *)dev);

    hr = dev->lpVtbl->CreateVertexBuffer(dev, sizeof(quad), 0, VFVF,
                                         D3DPOOL_MANAGED, &vbRead, NULL);
    if (FAILED(hr)) {
        printf("FAIL: CreateVertexBuffer(readable) -> 0x%08lX\n", (unsigned long)hr);
        return 2;
    }
    fill_quad(quad, 300.0f, 200.0f, 428.0f, 296.0f, 0xFF00FF00);
    if (SUCCEEDED(vbRead->lpVtbl->Lock(vbRead, 0, sizeof(quad), &p, 0))) {
        memcpy(p, quad, sizeof(quad));
        vbRead->lpVtbl->Unlock(vbRead);
    }

    hr = dev->lpVtbl->CreateVertexBuffer(dev, sizeof(quad), D3DUSAGE_WRITEONLY,
                                         VFVF, D3DPOOL_DEFAULT, &vbWrite, NULL);
    if (FAILED(hr)) {
        printf("FAIL: CreateVertexBuffer(write-only) -> 0x%08lX\n", (unsigned long)hr);
        return 2;
    }
    fill_quad(quad, 10.0f, 20.0f, 30.0f, 40.0f, 0xFF0000FF);
    if (SUCCEEDED(vbWrite->lpVtbl->Lock(vbWrite, 0, sizeof(quad), &p, 0))) {
        memcpy(p, quad, sizeof(quad));
        vbWrite->lpVtbl->Unlock(vbWrite);
    }

    for (frame = 0; frame < 3; ++frame) {
        dev->lpVtbl->Clear(dev, 0, NULL, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER,
                           0xFF102030, 1.0f, 0);
        dev->lpVtbl->BeginScene(dev);

        dev->lpVtbl->SetFVF(dev, VFVF);
        dev->lpVtbl->SetRenderState(dev, D3DRS_ALPHABLENDENABLE, TRUE);
        dev->lpVtbl->SetRenderState(dev, D3DRS_SRCBLEND, D3DBLEND_SRCALPHA);
        dev->lpVtbl->SetRenderState(dev, D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA);
        dev->lpVtbl->SetRenderState(dev, D3DRS_ZENABLE, D3DZB_FALSE);
        dev->lpVtbl->SetRenderState(dev, D3DRS_CULLMODE, D3DCULL_NONE);
        dev->lpVtbl->SetTextureStageState(dev, 0, D3DTSS_COLOROP, D3DTOP_MODULATE);
        dev->lpVtbl->SetTexture(dev, 0, NULL);

        fill_quad(quad, 100.0f, 50.0f, 228.0f, 146.0f, 0x80FF8040);
        dev->lpVtbl->DrawPrimitiveUP(dev, D3DPT_TRIANGLEFAN, 2, quad, sizeof(Vtx));

        dev->lpVtbl->SetStreamSource(dev, 0, vbRead, 0, sizeof(Vtx));
        dev->lpVtbl->DrawPrimitive(dev, D3DPT_TRIANGLEFAN, 0, 2);

        dev->lpVtbl->SetStreamSource(dev, 0, vbWrite, 0, sizeof(Vtx));
        dev->lpVtbl->DrawPrimitive(dev, D3DPT_TRIANGLEFAN, 0, 2);

        dev->lpVtbl->EndScene(dev);
        dev->lpVtbl->Present(dev, NULL, NULL, NULL, NULL);
    }

    /* ---- frame 3: the refusal paths ------------------------------------- */
    {
        IDirect3DVertexBuffer9 *vbDoomed = NULL, *vbRecycled = NULL;
        IDirect3DVertexBuffer9 *vbGap = NULL, *vbRing = NULL;
        Vtx big[100];
        int i;

        dev->lpVtbl->Clear(dev, 0, NULL, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER,
                           0xFF102030, 1.0f, 0);
        dev->lpVtbl->BeginScene(dev);
        dev->lpVtbl->SetFVF(dev, VFVF);

        /* draw 0 -- over the vertex cap. Must be refused BY NAME, not dropped. */
        for (i = 0; i < 100; ++i) {
            big[i].x = 1000.0f + i; big[i].y = 2000.0f + i;
            big[i].z = 0.0f; big[i].rhw = 1.0f;
            big[i].colour = 0xFF010203; big[i].u = 0.0f; big[i].v = 0.0f;
        }
        dev->lpVtbl->DrawPrimitiveUP(dev, D3DPT_TRIANGLEFAN, 98, big, sizeof(Vtx));

        /* draw 1 -- USE AFTER FREE. The device keeps the REAL buffer alive, so
         * this draw is legal Direct3D; only the proxy's wrapper has died. A
         * fresh buffer of the same size is allocated immediately afterwards to
         * give the allocator every chance to reuse the freed block. */
        hr = dev->lpVtbl->CreateVertexBuffer(dev, sizeof(quad),
                                             D3DUSAGE_WRITEONLY, VFVF,
                                             D3DPOOL_DEFAULT, &vbDoomed, NULL);
        if (FAILED(hr)) { printf("FAIL: CreateVertexBuffer(doomed) -> 0x%08lX\n", (unsigned long)hr); return 2; }
        fill_quad(quad, 777.0f, 888.0f, 779.0f, 890.0f, 0xFFAAAAAA);
        if (SUCCEEDED(vbDoomed->lpVtbl->Lock(vbDoomed, 0, sizeof(quad), &p, 0))) {
            memcpy(p, quad, sizeof(quad));
            vbDoomed->lpVtbl->Unlock(vbDoomed);
        }
        dev->lpVtbl->SetStreamSource(dev, 0, vbDoomed, 0, sizeof(Vtx));
        vbDoomed->lpVtbl->Release(vbDoomed);

        hr = dev->lpVtbl->CreateVertexBuffer(dev, sizeof(quad),
                                             D3DUSAGE_WRITEONLY, VFVF,
                                             D3DPOOL_DEFAULT, &vbRecycled, NULL);
        if (FAILED(hr)) { printf("FAIL: CreateVertexBuffer(recycled) -> 0x%08lX\n", (unsigned long)hr); return 2; }
        fill_quad(quad, 555.0f, 666.0f, 557.0f, 668.0f, 0xFFBBBBBB);
        if (SUCCEEDED(vbRecycled->lpVtbl->Lock(vbRecycled, 0, sizeof(quad), &p, 0))) {
            memcpy(p, quad, sizeof(quad));
            vbRecycled->lpVtbl->Unlock(vbRecycled);
        }
        /* Deliberately NOT bound. Stream 0 still names the dead wrapper. */
        dev->lpVtbl->DrawPrimitive(dev, D3DPT_TRIANGLEFAN, 0, 2);

        /* draw 2 -- two disjoint locked ranges, then a draw across the gap. A
         * hull would have claimed the gap and decoded calloc'd zeros. */
        hr = dev->lpVtbl->CreateVertexBuffer(dev, 256, 0, VFVF, D3DPOOL_MANAGED,
                                             &vbGap, NULL);
        if (FAILED(hr)) { printf("FAIL: CreateVertexBuffer(gap) -> 0x%08lX\n", (unsigned long)hr); return 2; }
        fill_quad(quad, 11.0f, 12.0f, 13.0f, 14.0f, 0xFF111111);
        if (SUCCEEDED(vbGap->lpVtbl->Lock(vbGap, 0, 2 * sizeof(Vtx), &p, 0))) {
            memcpy(p, quad, 2 * sizeof(Vtx));
            vbGap->lpVtbl->Unlock(vbGap);
        }
        if (SUCCEEDED(vbGap->lpVtbl->Lock(vbGap, 4 * sizeof(Vtx), 2 * sizeof(Vtx), &p, 0))) {
            memcpy(p, quad, 2 * sizeof(Vtx));
            vbGap->lpVtbl->Unlock(vbGap);
        }
        dev->lpVtbl->SetStreamSource(dev, 0, vbGap, 0, sizeof(Vtx));
        dev->lpVtbl->DrawPrimitive(dev, D3DPT_TRIANGLEFAN, 2, 2);

        /* draw 3 -- the dynamic ring idiom: Lock(0, 0, D3DLOCK_DISCARD). The
         * mapped extent is the whole buffer; the written extent is unknowable.
         * The data is still recovered, but the draw must carry a warning. */
        hr = dev->lpVtbl->CreateVertexBuffer(dev, 256,
                                             D3DUSAGE_DYNAMIC | D3DUSAGE_WRITEONLY,
                                             VFVF, D3DPOOL_DEFAULT, &vbRing, NULL);
        if (FAILED(hr)) { printf("FAIL: CreateVertexBuffer(ring) -> 0x%08lX\n", (unsigned long)hr); return 2; }
        fill_quad(quad, 41.0f, 42.0f, 43.0f, 44.0f, 0xFF222222);
        if (SUCCEEDED(vbRing->lpVtbl->Lock(vbRing, 0, 0, &p, D3DLOCK_DISCARD))) {
            memcpy(p, quad, sizeof(quad));
            vbRing->lpVtbl->Unlock(vbRing);
        }
        dev->lpVtbl->SetStreamSource(dev, 0, vbRing, 0, sizeof(Vtx));
        dev->lpVtbl->DrawPrimitive(dev, D3DPT_TRIANGLEFAN, 0, 2);

        /* draw 4 -- control. */
        dev->lpVtbl->SetStreamSource(dev, 0, vbRead, 0, sizeof(Vtx));
        dev->lpVtbl->DrawPrimitive(dev, D3DPT_TRIANGLEFAN, 0, 2);

        dev->lpVtbl->EndScene(dev);
        dev->lpVtbl->Present(dev, NULL, NULL, NULL, NULL);

        dev->lpVtbl->SetStreamSource(dev, 0, NULL, 0, 0);
        vbRing->lpVtbl->Release(vbRing);
        vbGap->lpVtbl->Release(vbGap);
        vbRecycled->lpVtbl->Release(vbRecycled);
    }

    vbWrite->lpVtbl->Release(vbWrite);
    vbRead->lpVtbl->Release(vbRead);
    dev->lpVtbl->Release(dev);
    d3d->lpVtbl->Release(d3d);
    DestroyWindow(hwnd);
    printf("PASS: 4 frames, 14 draws, released cleanly\n");
    return 0;
}
