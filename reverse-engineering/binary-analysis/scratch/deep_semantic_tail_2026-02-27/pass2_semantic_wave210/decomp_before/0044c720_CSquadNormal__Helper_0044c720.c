/* address: 0x0044c720 */
/* name: CSquadNormal__Helper_0044c720 */
/* signature: int __thiscall CSquadNormal__Helper_0044c720(void * this, int param_1, int param_2) */


int __thiscall CSquadNormal__Helper_0044c720(void *this,int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int local_8;

  local_8 = (int)(longlong)ROUND((float)param_1);
  param_1 = (int)(longlong)ROUND((float)param_2);
  iVar2 = (int)(local_8 + (local_8 >> 0x1f & 7U)) >> 3;
  iVar1 = (int)(param_1 + (param_1 >> 0x1f & 7U)) >> 3;
  if ((((-1 < iVar2) && (-1 < iVar1)) && (iVar2 < 0x40)) && (iVar1 < 0x40)) {
    return *(int *)((int)this + (iVar2 * 0x40 + iVar1) * 4 + 8);
  }
  return 0;
}
