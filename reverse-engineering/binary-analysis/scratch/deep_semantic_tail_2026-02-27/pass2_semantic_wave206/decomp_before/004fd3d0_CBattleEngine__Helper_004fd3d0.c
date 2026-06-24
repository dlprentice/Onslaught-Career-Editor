/* address: 0x004fd3d0 */
/* name: CBattleEngine__Helper_004fd3d0 */
/* signature: int __thiscall CBattleEngine__Helper_004fd3d0(void * this, int param_1, int param_2) */


int __thiscall CBattleEngine__Helper_004fd3d0(void *this,int param_1,int param_2)

{
  int iVar1;

  if (((*(int *)((int)this + 0x164) == 0) || (*(int *)(*(int *)((int)this + 0x164) + 0x128) == 0))
     || (param_1 != 2)) {
    if (param_1 == 0) {
      if ((*(int *)((int)this + 0x138) != 1) && (*(int *)((int)this + 0x138) != 6)) {
        return 0;
      }
    }
    else {
      if (param_1 == 1) {
        if (*(int *)((int)this + 0x138) == 0) {
          return 1;
        }
        iVar1 = *(int *)((int)this + 0x138) + -6;
      }
      else {
        if (param_1 != 6) {
          return 0;
        }
        iVar1 = *(int *)((int)this + 0x138);
        if (iVar1 == 1) {
          return 1;
        }
      }
      if (iVar1 != 0) {
        return 0;
      }
    }
  }
  return 1;
}
