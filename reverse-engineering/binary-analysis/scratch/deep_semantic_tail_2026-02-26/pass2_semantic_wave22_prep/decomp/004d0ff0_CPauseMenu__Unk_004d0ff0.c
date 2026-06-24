/* address: 0x004d0ff0 */
/* name: CPauseMenu__Unk_004d0ff0 */
/* signature: void __thiscall CPauseMenu__Unk_004d0ff0(void * this, int param_1, int param_2) */


void __thiscall CPauseMenu__Unk_004d0ff0(void *this,int param_1,int param_2)

{
  int iVar1;
  int unaff_EDI;
  float fVar2;
  undefined4 uVar3;
  undefined4 uVar4;

  *(undefined4 *)((int)this + 0xc) = 0;
  *(undefined4 *)((int)this + 0x10) = 1;
  *(undefined4 *)((int)this + 0x38) = 0;
  fVar2 = PLATFORM__GetSysTimeFloat();
  *(float *)((int)this + 0x28) = fVar2;
  fVar2 = PLATFORM__GetSysTimeFloat();
  *(float *)((int)this + 0x2c) = fVar2;
  *(undefined4 *)((int)this + 0x24) = 0;
  CUnit__Unk_004e5c90((void *)((int)this + 0x14),(void *)0x0,unaff_EDI);
  CMenuItemRange__ResetIterator();
  *(uint *)((int)this + 0x48) = (uint)(param_1 == 0);
  iVar1 = CGame__CountActiveSlots_A(0x8a9a98);
  if (iVar1 == 0) {
    iVar1 = CGame__CountActiveSlots_B(0x8a9a98);
    if (iVar1 != 0) goto LAB_004d1075;
    iVar1 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
    if (iVar1 == 0) goto LAB_004d1075;
  }
  else {
LAB_004d1075:
    if (DAT_008a9d38 < 900) {
      uVar4 = 1;
      goto LAB_004d1087;
    }
  }
  uVar4 = 0;
LAB_004d1087:
  uVar3 = 0x3fc4f9;
  CUnit__Unk_004e5c90((void *)((int)this + 0x14),(void *)0x0,0x3fc4f9);
  CMenuItemRange__SetItemEnabled(uVar3,uVar4);
  return;
}
