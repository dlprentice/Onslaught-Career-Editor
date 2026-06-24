/* address: 0x0047a8b0 */
/* name: CGillMHead__TryTransitionIdleToOpen */
/* signature: int __fastcall CGillMHead__TryTransitionIdleToOpen(int param_1) */


int __fastcall CGillMHead__TryTransitionIdleToOpen(int param_1)

{
  int iVar1;
  int iVar2;
  int unaff_EDI;

  iVar1 = CGillMHead__Helper_004f4530((void *)param_1,0x62ca48,unaff_EDI);
  iVar2 = (**(code **)(*(int *)(param_1 + 8) + 0x58))();
  if (iVar2 != iVar1) {
    return 0;
  }
  iVar1 = CUnit__Unk_004fbcb0((void *)param_1);
  if (iVar1 == 0) {
    return 0;
  }
  CGillMHead__Helper_004f4560((void *)param_1,&DAT_00623bb4,1,0,unaff_EDI);
  return 1;
}
