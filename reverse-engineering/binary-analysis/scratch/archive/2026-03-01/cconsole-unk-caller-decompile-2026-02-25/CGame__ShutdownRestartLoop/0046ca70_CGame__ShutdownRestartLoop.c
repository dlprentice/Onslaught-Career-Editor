/* address: 0x0046ca70 */
/* name: CGame__ShutdownRestartLoop */
/* signature: void __fastcall CGame__ShutdownRestartLoop(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Source-aligned mapping to CGame::ShutdownRestartLoop(). Tears down per-level/restart runtime
   state: stops music/scripts, frees UI/runtime allocations and random stream, clears
   map/fx/atmospherics/script events, shuts down EVENT_MANAGER, and resets loading/progress helpers.
    */

void __fastcall CGame__ShutdownRestartLoop(void *this)

{
  void *obj;
  int iVar1;
  char *unaff_ESI;
  int *piVar2;

  iVar1 = 4;
  if ((*(int *)((int)this + 0x34) == 4) && (DAT_0083d448 != 0)) {
    DAT_0066e8c0 = 1;
  }
  if (DAT_00662dcc != 0) {
    CMusic__Stop(&DAT_00889a48);
  }
  CScriptObjectCode__Reset();
  if (*(int *)((int)this + 0x34) == 4) {
    CConsole__SetLoading(&DAT_00663498,'\x01',1);
  }
  DAT_0066e8c0 = 0;
  CConsole__RenderLoadingScreen(&DAT_00663498,0,'\0');
  CConsole__Status(&DAT_00663498,s_Freeing_Up_Level_Resources____0062bf20);
  CMonitor__Shutdown_Core(this);
  if (*(int **)((int)this + 0x2e4) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x2e4) + 4))(1);
    *(undefined4 *)((int)this + 0x2e4) = 0;
  }
  if (*(int **)((int)this + 0x2e8) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x2e8) + 4))(1);
    *(undefined4 *)((int)this + 0x2e8) = 0;
  }
  piVar2 = (int *)((int)this + 0x2b4);
  do {
    if ((undefined4 *)*piVar2 != (undefined4 *)0x0) {
      (*(code *)**(undefined4 **)*piVar2)(1);
      *piVar2 = 0;
    }
    piVar2 = piVar2 + 1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  if (*(int **)((int)this + 0x2f0) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x2f0) + 4))(1);
    *(undefined4 *)((int)this + 0x2f0) = 0;
  }
  if (*(int **)((int)this + 0x2ec) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x2ec) + 4))(1);
    *(undefined4 *)((int)this + 0x2ec) = 0;
  }
  if (*(int **)((int)this + 0x2f4) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x2f4) + 4))(1);
    *(undefined4 *)((int)this + 0x2f4) = 0;
  }
  if (*(int **)((int)this + 0x2fc) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x2fc) + 4))(1);
    *(undefined4 *)((int)this + 0x2fc) = 0;
  }
  if (*(void **)((int)this + 0x304) != (void *)0x0) {
    OID__FreeObject(*(void **)((int)this + 0x304));
    *(undefined4 *)((int)this + 0x304) = 0;
  }
  if (*(undefined4 **)((int)this + 0x2f8) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)this + 0x2f8))(1);
    *(undefined4 *)((int)this + 0x2f8) = 0;
  }
  DebugTrace(unaff_ESI);
  *(undefined4 *)((int)this + 0x114) = 0;
  CConsole__SetLoadingFraction(&DAT_00663498,0.1);
  CUnitAI__Unk_00441e50(&DAT_0066ffb0);
  CConsole__SetLoadingFraction(&DAT_00663498,0.2);
  CWorld__Unk_0050ada0(&DAT_00855090);
  _DAT_008969ac = 0x3f800000;
  CConsole__SetLoadingFraction(&DAT_00663498,0.3);
  CDXTrees__Reset();
  CConsole__SetLoadingFraction(&DAT_00663498,0.4);
  CMapWho__Destroy();
  CConsole__SetLoadingFraction(&DAT_00663498,0.5);
  Atmospherics__Shutdown();
  CConsole__SetLoadingFraction(&DAT_00663498,0.6);
  CWorldPhysicsManager__Unk_00510740();
  CConsole__SetLoadingFraction(&DAT_00663498,0.7);
  iVar1 = DAT_009c63e8;
  while (DAT_009c63e8 = iVar1, DAT_009c63e8 != 0) {
    iVar1 = *(int *)(DAT_009c63e8 + 0x68);
    CParticle__Destroy();
    *(int *)(DAT_009c63e8 + 0x68) = DAT_009c63f0;
    DAT_009c63f0 = DAT_009c63e8;
  }
  CParticleManager__Unk_004caf30();
  CParticleManager__Unk_004cb080();
  CParticleManager__CleanupHandles();
  obj = DAT_009c63f4;
  if (DAT_009c63f4 != (void *)0x0) {
    CParticleManager__Shutdown();
    OID__FreeObject(obj);
  }
  DAT_009c63f4 = (void *)0x0;
  CConsole__SetLoadingFraction(&DAT_00663498,0.8);
  CScriptEventNB__DestroyAllEvents();
  CConsole__SetLoadingFraction(&DAT_00663498,0.9);
  CEventManager__Shutdown(&EVENT_MANAGER);
  CConsole__SetLoadingFraction(&DAT_00663498,1.0);
  CConsole__Unk_0042d3b0();
  return;
}
