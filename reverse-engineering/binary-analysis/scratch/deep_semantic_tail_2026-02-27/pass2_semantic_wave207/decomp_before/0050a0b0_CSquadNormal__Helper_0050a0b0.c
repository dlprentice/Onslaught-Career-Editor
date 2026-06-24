/* address: 0x0050a0b0 */
/* name: CSquadNormal__Helper_0050a0b0 */
/* signature: uint __thiscall CSquadNormal__Helper_0050a0b0(void * this, int param_1, int param_2) */


uint __thiscall CSquadNormal__Helper_0050a0b0(void *this,int param_1,int param_2)

{
  if (*(int *)((int)this + 0x9c) == 0) {
    return 0;
  }
  return *(uint *)((int)this + 0xa8) & *(uint *)(param_1 + 0x34);
}
