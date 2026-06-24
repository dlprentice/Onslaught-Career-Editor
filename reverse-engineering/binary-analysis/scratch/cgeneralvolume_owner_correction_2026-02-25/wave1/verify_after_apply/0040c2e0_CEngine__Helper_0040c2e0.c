/* address: 0x0040c2e0 */
/* name: CEngine__Helper_0040c2e0 */
/* signature: int __thiscall CEngine__Helper_0040c2e0(void * this, int param_1, int param_2) */


int __thiscall CEngine__Helper_0040c2e0(void *this,int param_1,int param_2)

{
  int iVar1;
  int unaff_EDI;

  iVar1 = CMonitor__Unk_00412050(*(void **)((int)this + 0x57c),(void *)param_1,unaff_EDI);
  if (iVar1 != 0) {
    *(undefined4 *)((int)this + 0x5d8) = 0;
    return 1;
  }
  iVar1 = CMonitor__Unk_004140d0(*(void **)((int)this + 0x578),(void *)param_1,unaff_EDI);
  if (iVar1 != 0) {
    *(undefined4 *)((int)this + 0x5d8) = 0;
    return 1;
  }
  return 0;
}
