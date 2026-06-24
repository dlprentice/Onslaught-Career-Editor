/* address: 0x0058a014 */
/* name: CTexture__HandleDirective_Else */
/* signature: int __fastcall CTexture__HandleDirective_Else(int param_1) */


int __fastcall CTexture__HandleDirective_Else(int param_1)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  char *pcVar4;

  piVar1 = *(int **)(*(int *)(param_1 + 0x50) + 0x38);
  if (piVar1 == (int *)0x0) {
    pcVar4 = "unexpected #else";
    iVar3 = 0x5e5;
  }
  else {
    if (piVar1[2] == 0) {
      uVar2 = 0;
      if ((*piVar1 == 0) && (piVar1[1] != 0)) {
        uVar2 = 1;
      }
      *(undefined4 *)(param_1 + 0x3c) = uVar2;
      *piVar1 = 1;
      piVar1[2] = 1;
      return 0;
    }
    pcVar4 = "unexpected #else following #else";
    iVar3 = 0x5ea;
  }
  CTexture__Helper_0058c893((void *)(param_1 + 4),param_1 + 0x60,iVar3,(int)pcVar4);
  *(undefined4 *)(param_1 + 0x2c) = 1;
  return -0x7fffbffb;
}
