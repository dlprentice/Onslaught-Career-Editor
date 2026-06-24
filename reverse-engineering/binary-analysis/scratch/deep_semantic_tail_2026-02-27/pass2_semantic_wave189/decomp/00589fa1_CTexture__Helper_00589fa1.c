/* address: 0x00589fa1 */
/* name: CTexture__Helper_00589fa1 */
/* signature: int __thiscall CTexture__Helper_00589fa1(void * this, int param_1, int param_2) */


int __thiscall CTexture__Helper_00589fa1(void *this,int param_1,int param_2)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  char *pcVar4;

  piVar1 = *(int **)(*(int *)((int)this + 0x50) + 0x38);
  if (piVar1 == (int *)0x0) {
    pcVar4 = "unexpected #elif";
    iVar3 = 0x5e4;
  }
  else {
    if (piVar1[2] == 0) {
      if (((param_1 == 0) || (*piVar1 != 0)) || (piVar1[1] == 0)) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
      *(undefined4 *)((int)this + 0x3c) = uVar2;
      if (param_1 != 0) {
        *piVar1 = 1;
      }
      return 0;
    }
    pcVar4 = "unexpected #elif following #else";
    iVar3 = 0x5e9;
  }
  CTexture__Helper_0058c893((void *)((int)this + 4),(int)this + 0x60,iVar3,(int)pcVar4);
  *(undefined4 *)((int)this + 0x2c) = 1;
  return -0x7fffbffb;
}
