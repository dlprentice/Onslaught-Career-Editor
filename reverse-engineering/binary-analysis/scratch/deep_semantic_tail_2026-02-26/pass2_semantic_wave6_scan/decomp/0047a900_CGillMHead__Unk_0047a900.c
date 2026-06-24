/* address: 0x0047a900 */
/* name: CGillMHead__Unk_0047a900 */
/* signature: int __fastcall CGillMHead__Unk_0047a900(int param_1) */


int __fastcall CGillMHead__Unk_0047a900(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int unaff_EBX;

  piVar1 = (int *)(param_1 + 8);
  iVar2 = (**(code **)(*(int *)(param_1 + 8) + 0x58))();
  if (iVar2 == -1) {
    return 1;
  }
  iVar2 = CGillMHead__Helper_004f4530((void *)param_1,0x623bb4,unaff_EBX);
  iVar3 = (**(code **)(*piVar1 + 0x58))();
  if (iVar3 != iVar2) {
    iVar2 = CGillMHead__Helper_004f4530((void *)param_1,0x624438,unaff_EBX);
    iVar3 = (**(code **)(*piVar1 + 0x58))();
    if (iVar3 != iVar2) {
      iVar2 = CGillMHead__Helper_004f4530((void *)param_1,0x6289e4,unaff_EBX);
      iVar3 = (**(code **)(*piVar1 + 0x58))();
      if (iVar3 == iVar2) {
        CGillMHead__Helper_004f4560((void *)param_1,&DAT_0062ca48,1,1,unaff_EBX);
      }
      return 0;
    }
    iVar2 = CVBufTexture__Helper_004fd760(param_1);
    if (iVar2 != 0) {
      CGillMHead__Helper_004f4560((void *)param_1,s_close_006289e4,1,0,unaff_EBX);
      return 0;
    }
  }
  CGillMHead__Helper_004f4560((void *)param_1,s_attack_00624438,1,0,unaff_EBX);
  return 0;
}
