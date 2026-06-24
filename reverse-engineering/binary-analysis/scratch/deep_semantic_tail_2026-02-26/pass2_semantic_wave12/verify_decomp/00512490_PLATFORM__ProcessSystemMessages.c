/* address: 0x00512490 */
/* name: PLATFORM__ProcessSystemMessages */
/* signature: int __thiscall PLATFORM__ProcessSystemMessages(void * this, void * param_1, bool param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall PLATFORM__ProcessSystemMessages(void *this,void *param_1,bool param_2)

{
  LPMSG lpMsg;
  int iVar1;
  int iVar2;
  int unaff_EDI;
  double dVar3;
  double dVar4;

  iVar2 = 1;
  lpMsg = (LPMSG)((int)this + 0x33494);
  if (*(int *)((int)this + 0x32e48) == 0) {
    iVar1 = GetMessageA(lpMsg,(HWND)0x0,0,0);
  }
  else {
    iVar1 = PeekMessageA(lpMsg,(HWND)0x0,0,0,1);
  }
  if (iVar1 != 0) {
    iVar1 = TranslateAcceleratorA
                      (*(HWND *)((int)this + 0x32e94),*(HACCEL *)((int)this + 0x334b0),lpMsg);
    if (iVar1 == 0) {
      TranslateMessage(lpMsg);
      DispatchMessageA(lpMsg);
      iVar2 = 1;
    }
    goto LAB_00512603;
  }
  if ((*(int *)((int)this + 0x32e48) == 0) || (*(int *)((int)this + 0x32e4c) == 0))
  goto LAB_00512603;
  iVar2 = 0;
  iVar1 = (**(code **)(**(int **)((int)this + 0x32ea0) + 0xc))(*(int **)((int)this + 0x32ea0));
  if (iVar1 < 0) {
    if (iVar1 == -0x7789f797) {
      if (*(int *)((int)this + 0x32e44) != 0) {
        iVar2 = *(int *)((int)this + 0x32e40) * 0x516c;
        (**(code **)(**(int **)((int)this + 0x32e9c) + 0x20))
                  (*(int **)((int)this + 0x32e9c),*(int *)((int)this + 0x32e40),
                   (int)this + iVar2 + 0x450);
        *(undefined4 *)((int)this + 0x32e60) = *(undefined4 *)((int)this + iVar2 + 0x45c);
      }
      iVar2 = CD3DApplication__Reset3DEnvironment(this,(void *)0x1,0,unaff_EDI);
      if (iVar2 < 0) {
        SendMessageA(DAT_00888a44,0x10,0,0);
      }
    }
    iVar2 = 1;
  }
  dVar3 = CD3DApplication__Helper_0052cd20(5);
  dVar4 = CD3DApplication__Helper_0052cd20(6);
  if ((double)_DAT_005d856c == dVar4) {
    if (*(int *)((int)this + 0x32e50) != 0) {
      return 0;
    }
LAB_005125db:
    if (*(int *)((int)this + 0x32e54) == 0) goto LAB_00512603;
  }
  else if (*(int *)((int)this + 0x32e50) == 0) goto LAB_005125db;
  *(undefined4 *)((int)this + 0x32e54) = 0;
  *(float *)((int)this + 0x33020) = (float)dVar4;
  *(float *)((int)this + 0x3301c) = (float)dVar3;
LAB_00512603:
  iVar1 = 0;
  do {
    PlatformInput__PollPadState(this,iVar1,SUB41(param_1,0));
    iVar1 = iVar1 + 1;
  } while (iVar1 < 4);
  PTR_DAT_0063dc1c = (undefined *)&DAT_00855424;
  return iVar2;
}
