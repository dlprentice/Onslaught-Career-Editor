/* address: 0x0050a0b0 */
/* name: CSquadNormal__HasActiveMaskMatchWithTarget */
/* signature: uint __thiscall CSquadNormal__HasActiveMaskMatchWithTarget(void * this, int param_1, int param_2) */


uint __thiscall CSquadNormal__HasActiveMaskMatchWithTarget(void *this,int param_1,int param_2)

{
  if (*(int *)((int)this + 0x9c) == 0) {
    return 0;
  }
  return *(uint *)((int)this + 0xa8) & *(uint *)(param_1 + 0x34);
}
