/* address: 0x0046e240 */
/* name: CGame__RunLevel */
/* signature: int __thiscall CGame__RunLevel(void * this, int aLevel) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Source-aligned mapping to CGame::RunLevel(SINT). Top-level level driver: init/startup checks,
   InitRestartLoop + LoadResources + one-off setup/HUD texture load, restart-loop orchestration via
   CGame__RestartLoopRunLevel, and final shutdown/quit-code return. */

int __thiscall CGame__RunLevel(void *this,int aLevel)

{
  bool bVar1;
  int iVar2;
  int iVar3;

  *(undefined4 *)((int)this + 0x24) = 0;
  if (DAT_0083d448 != 0) {
    DAT_0066e8c0 = 1;
  }
  CConsole__SetLoading(&DAT_00663498,'\x01',1);
  DAT_0066e8c0 = 0;
  if (DAT_00662dcc != 0) {
    CMusic__Stop(&DAT_00889a48);
  }
  if (DAT_00662f40 != 0) {
    CUnit__Unk_004e2c50(&DAT_00896988);
  }
  *(undefined4 *)((int)this + 0xa08) = 1;
  iVar2 = CGame__Init(this);
  if (iVar2 == 0) {
    (**(code **)(*(int *)this + 8))();
    return 3;
  }
  *(int *)((int)this + 0x2a0) = aLevel;
  iVar2 = CGame__InitRestartLoop(this);
  if (iVar2 == 0) {
    CGame__ShutdownRestartLoop(this);
    return 3;
  }
  _DAT_008552fc = 0xffffffff;
  _DAT_00855300 = 0xffffffff;
  _DAT_00855304 = 0xffffffff;
  _DAT_00855308 = 0xffffffff;
  iVar2 = CGame__LoadResources(aLevel,0);
  if (iVar2 == 0) {
    CConsole__Unk_0042c750(s_game_resources_0062c140);
  }
  CConsole__SetLoadingRange(&DAT_00663498,50.0,65.0);
  CDXEngine__VFunc_02_0053d6d0(0x89c9a0);
  CConsole__SetLoadingFraction(&DAT_00663498,0.33);
  CGameInterface__Unk_00472a10(0x679fa8);
  CConsole__SetLoadingFraction(&DAT_00663498,0.66);
  CHud__LoadTextures();
  CConsole__SetLoadingFraction(&DAT_00663498,1.0);
  bVar1 = true;
  CConsole__SetLoadingRange(&DAT_00663498,65.0,80.0);
  iVar2 = 0;
  do {
    CUnitAI__Unk_004b7320(*(int *)((int)this + 0x2ec));
    CMessageLog__Unk_004b8e70(*(int *)((int)this + 0x2f0));
    CPauseMenu__Unk_004d0510(*(int *)((int)this + 0x2f4));
    iVar3 = CGame__RestartLoopRunLevel(this,aLevel);
    *(int *)((int)this + 0x34) = iVar3;
    CGame__ShutdownRestartLoop(this);
    if ((DAT_0083d454 == 4) && (iVar2 < 5)) {
      *(undefined4 *)((int)this + 0x34) = 4;
      iVar2 = iVar2 + 1;
    }
    if (*(int *)((int)this + 0x34) == 4) {
      *(undefined4 *)((int)this + 0x24) = 1;
      CMusic__Stop(&DAT_00889a48);
      iVar3 = CGame__InitRestartLoop(this);
      if (iVar3 == 0) {
        CGame__ShutdownRestartLoop(this);
LAB_0046e40e:
        bVar1 = false;
      }
    }
    else {
      if (*(int *)((int)this + 0x34) != 3) goto LAB_0046e40e;
      FatalError_LocalizedStringId('\0',0xf5,-1);
    }
    *(undefined4 *)((int)this + 0xa08) = 0;
    if (!bVar1) {
      *(undefined4 *)((int)this + 0x24) = 0;
      CConsole__SetLoadingRange(&DAT_00663498,0.0,50.0);
      (**(code **)(*(int *)this + 8))();
      return *(int *)((int)this + 0x34);
    }
  } while( true );
}
