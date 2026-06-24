/* address: 0x004e4480 */
/* name: CSquadNormal__Helper_004e4480 */
/* signature: int __thiscall CSquadNormal__Helper_004e4480(void * this, int param_1, int param_2) */


int __thiscall CSquadNormal__Helper_004e4480(void *this,int param_1,int param_2)

{
  int iVar1;

  if ((((*(int *)((int)this + 0x3f4) != 0) && (iVar1 = *(int *)((int)this + 0x3d0), iVar1 != 0)) &&
      ((*(int *)((int)this + 0x3d8) < *(int *)(iVar1 + 0xc) || (*(int *)(iVar1 + 0x24) != 0)))) &&
     ((*(uint *)(param_1 + 0x34) & *(uint *)((int)this + 0x3f0)) != 0)) {
    return 1;
  }
  return 0;
}
