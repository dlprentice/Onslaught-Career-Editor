/* address: 0x0058e3c3 */
/* name: CTexture__FlushPendingConstantTableWrites */
/* signature: int __thiscall CTexture__FlushPendingConstantTableWrites(void * this, int param_1, int param_2) */


int __thiscall CTexture__FlushPendingConstantTableWrites(void *this,int param_1,int param_2)

{
  int *piVar1;
  uint uVar2;
  int iVar3;

  piVar1 = *(int **)((int)this + 8);
  if (piVar1 != (int *)0x0) {
    uVar2 = *(uint *)((int)this + 100);
    if (uVar2 < *(uint *)((int)this + 0x5c)) {
      *(int *)((int)this + 0x30) = param_1;
      iVar3 = (**(code **)(*piVar1 + 0x10))
                        (piVar1,*(undefined4 *)(param_1 + 0x10),*(undefined4 *)(param_1 + 0x14),
                         *(int *)((int)this + 0x58) + uVar2 * 4,*(uint *)((int)this + 0x5c) - uVar2)
      ;
      if (iVar3 < 0) {
        *(undefined4 *)((int)this + 0x4c) = 1;
        *(undefined4 *)((int)this + 0x50) = 1;
      }
      *(undefined4 *)((int)this + 100) = *(undefined4 *)((int)this + 0x5c);
      return iVar3;
    }
  }
  return 0;
}
