/* address: 0x0056fdc0 */
/* name: CFastVB__Helper_0056fdc0 */
/* signature: int __thiscall CFastVB__Helper_0056fdc0(void * this, int param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CFastVB__Helper_0056fdc0(void *this,int param_1,int param_2,int param_3)

{
  float fVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;

  iVar5 = 0;
  if (*(int *)(param_1 + 4) == 0) {
    iVar4 = 0;
  }
  else {
    iVar4 = *(int *)(param_1 + 8) - *(int *)(param_1 + 4) >> 2;
  }
  if (*(char *)((int)this + 0x1c) == '\0') {
    uVar2 = __ftol();
  }
  else {
    uVar2 = CFastVB__Helper_0056fce0(param_1,param_2);
    *(undefined1 *)((int)this + 0x1c) = 0;
  }
  if (uVar2 == 0xffffffff) {
    uVar2 = __ftol();
  }
  uVar3 = uVar2;
  do {
    if (*(int *)(*(int *)(*(int *)(param_1 + 4) + uVar3 * 4) + 0xc) < 0) {
      iVar5 = *(int *)(*(int *)(param_1 + 4) + uVar3 * 4);
      break;
    }
    uVar3 = uVar3 + 1;
    if (iVar4 <= (int)uVar3) {
      uVar3 = 0;
    }
  } while (uVar3 != uVar2);
  fVar1 = *(float *)((int)this + 0x18) + _DAT_005e6a30;
  *(float *)((int)this + 0x18) = fVar1;
  if (_DAT_005e6a34 < fVar1) {
    *(undefined4 *)((int)this + 0x18) = 0x3d4ccccd;
  }
  return iVar5;
}
