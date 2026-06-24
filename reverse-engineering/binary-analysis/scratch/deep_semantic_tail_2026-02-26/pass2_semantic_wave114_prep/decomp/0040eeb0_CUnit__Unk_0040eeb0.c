/* address: 0x0040eeb0 */
/* name: CUnit__Unk_0040eeb0 */
/* signature: int __fastcall CUnit__Unk_0040eeb0(int param_1) */


int __fastcall CUnit__Unk_0040eeb0(int param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  void *unaff_EDI;
  char *pcVar4;

  iVar1 = (**(code **)(*(int *)(param_1 + 8) + 0x58))();
  if (iVar1 != -1) {
    pcVar4 = s_flytowalk_006234bc;
    pvVar2 = (void *)(**(code **)(**(int **)(param_1 + 0x30) + 0x24))();
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar4,unaff_EDI);
    if (iVar1 == iVar3) {
      CGillMHead__Helper_004f4560((void *)param_1,&DAT_006235a0,1,1,(int)unaff_EDI);
      return 0;
    }
    pcVar4 = s_walktofly_006234b0;
    pvVar2 = (void *)(**(code **)(**(int **)(param_1 + 0x30) + 0x24))();
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar4,unaff_EDI);
    if (iVar1 == iVar3) {
      CGillMHead__Helper_004f4560((void *)param_1,&PTR_DAT_0062359c,1,1,(int)unaff_EDI);
    }
  }
  return 0;
}
