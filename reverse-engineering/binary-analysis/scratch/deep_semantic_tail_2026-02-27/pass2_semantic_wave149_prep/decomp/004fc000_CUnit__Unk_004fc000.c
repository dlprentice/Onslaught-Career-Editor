/* address: 0x004fc000 */
/* name: CUnit__Unk_004fc000 */
/* signature: int __fastcall CUnit__Unk_004fc000(int param_1) */


int __fastcall CUnit__Unk_004fc000(int param_1)

{
  int *piVar1;
  bool bVar2;
  int iVar3;
  undefined3 extraout_var;

  if (*(int *)(param_1 + 0x140) == 0) {
    if (*(int *)(param_1 + 0x144) != 0) {
      if (*(int *)(*(int *)(param_1 + 0x164) + 0x110) == 0) {
        piVar1 = *(int **)(param_1 + 0x18c);
        if (piVar1 == (int *)0x0) {
          iVar3 = 0;
        }
        else {
          iVar3 = *piVar1;
        }
        while (iVar3 != 0) {
          bVar2 = CUnit__Helper_004e4420(iVar3);
          if (CONCAT31(extraout_var,bVar2) != 0) {
            return 0;
          }
          piVar1 = (int *)piVar1[1];
          if (piVar1 == (int *)0x0) {
            iVar3 = 0;
          }
          else {
            iVar3 = *piVar1;
          }
        }
      }
      return 1;
    }
  }
  else if ((*(int *)(param_1 + 0x1e8) != 0) &&
          (iVar3 = CUnit__Helper_00509f70(*(int *)(param_1 + 0x140)), iVar3 != 0)) {
    return 1;
  }
  return 0;
}
