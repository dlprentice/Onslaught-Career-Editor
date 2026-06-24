/* address: 0x0053ecc0 */
/* name: CDXEngine__PostRender */
/* signature: int __thiscall CDXEngine__PostRender(void * this, void * viewport) */


/* Source-aligned with CDXEngine::PostRender(CViewport*). Post-view overlay/UI pass: HUD and shared
   HUD, message logs/pause UI, debug overlays/console traces, cheat/frontend update checks,
   render-state cleanup, and end-of-frame housekeeping. */

int __thiscall CDXEngine__PostRender(void *this,void *viewport)

{
  bool bVar1;
  int iVar2;
  void *pvVar3;
  char cVar4;
  int *piVar5;
  short *psVar6;
  void *unaff_EBP;
  int number;
  char *unaff_EDI;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;

  pvVar3 = viewport;
  PLATFORM__BeginScene();
  D3DDevice__SetViewport(viewport);
  *(undefined4 *)((int)this + 0x474) = *(undefined4 *)viewport;
  if (DAT_0089d680 == '\0') {
    CDXEngine__Helper_00487bc0(0x8aa4e8);
    D3DDevice__SetViewport(viewport);
    number = 0;
    *(undefined4 *)((int)this + 0x474) = *(undefined4 *)viewport;
    iVar2 = DAT_0089c9ac;
    bVar1 = false;
    if (0 < DAT_0089c9ac) {
      viewport = &DAT_0089ce08;
      do {
        if (*(int *)viewport != 0) {
          piVar5 = CGame__GetCamera(&DAT_008a9a98,number);
          cVar4 = (**(code **)(*piVar5 + 0x1c))();
          if (cVar4 != '\0') {
            bVar1 = true;
          }
        }
        number = number + 1;
        viewport = (void *)((int)viewport + 4);
      } while (number < iVar2);
      if (bVar1) {
        CDXEngine__Helper_00487d10(&DAT_008aa4e8,pvVar3,unaff_EBP);
      }
    }
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
    DAT_009c68ad = 0;
    DAT_009c6910 = 1;
    D3DStateCache__SetState114Raw(0,1,3);
    D3DStateCache__SetState114Raw(0,2,3);
    D3DStateCache__SetStateCached(0,1,4);
    D3DStateCache__SetStateCached(0,3,0);
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    DAT_00679b40 = 1;
    CMessageLog__Unk_004b93f0(DAT_008a9d88);
    CDXEngine__Helper_0048f620();
    CEngine__Unk_004d11d0(DAT_008a9d8c);
    DAT_00679b40 = 0;
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
    DAT_009c68ad = 0;
    DAT_009c6910 = 1;
    D3DStateCache__SetState114Raw(0,1,3);
    D3DStateCache__SetState114Raw(0,2,3);
    D3DStateCache__SetMipFilterPoint(0);
    D3DStateCache__SetState114Raw(0,6,2);
    D3DStateCache__SetState114Raw(0,5,2);
    RenderState_Set(0x17,4);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  }
  if (DAT_009c7490 != '\0') {
    uVar12 = 0x3f800000;
    uVar11 = 0;
    uVar10 = 0;
    psVar6 = Text__AsciiToWideScratch(s_Render_queue_active_006505fc);
    uVar9 = 0xffffffff;
    uVar8 = 0x42200000;
    uVar7 = 0;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar7,uVar8,uVar9,psVar6,uVar10,uVar11,uVar12);
  }
  D3DStateCache__SetState114Raw(0,1,1);
  D3DStateCache__SetState114Raw(0,2,1);
  DAT_009c68ac = 1;
  DAT_009c690d = 1;
  DAT_009c68ad = 1;
  DAT_009c6910 = 1;
  CDXEngine__Helper_00488090(0x8aa4e8);
  if (0 < *(int *)((int)this + 0x4cc)) {
    *(int *)((int)this + 0x4cc) = *(int *)((int)this + 0x4cc) + -0xf;
  }
  if (*(int *)((int)this + 0x4d0) != -1) {
    *(int *)((int)this + 0x4cc) = *(int *)((int)this + 0x4d0);
    *(undefined4 *)((int)this + 0x4d0) = 0xffffffff;
  }
  CDXEngine__Helper_00482050(0x8aa4e8);
  CDXEngine__CaptureAviFrame();
  CVBufTexture__ReleaseAllUnlocked();
  DAT_009c68ad = 1;
  DAT_009c6910 = 1;
  if ((*(byte *)((int)this + 0x4b4) & 0x40) != 0) {
    CDXEngine__Unk_00549290(0x9c3df0);
  }
  CGame__RenderDebugMemoryAndSelectionInfo(0x8a9a98);
  FrontendUpdate_CheatChecks();
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  DebugTrace(unaff_EDI);
  DAT_009c68ac = 1;
  DAT_009c690d = 1;
  if (DAT_0089d680 == '\0') {
    CDXEngine__Helper_00472f10(&DAT_00679fa8);
  }
  PLATFORM__EndScene();
  *(undefined4 *)((int)this + 0xafc) = 0;
  CDXEngine__Helper_00501540();
  if (DAT_0089d688 != '\0') {
    CEngine__Unk_005015c0();
  }
  return 0;
}
