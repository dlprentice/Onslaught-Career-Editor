/* address: 0x00423960 */
/* name: CMeshPart__Helper_00423960 */
/* signature: bool __thiscall CMeshPart__Helper_00423960(void * this, int param_1, int param_2, int param_3, int param_4) */


bool __thiscall
CMeshPart__Helper_00423960(void *this,int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;

  iVar2 = param_2 * param_3;
  *(int *)((int)this + 8) = *(int *)((int)this + 8) + iVar2;
  iVar1 = DXMemBuffer__ReadBytes(param_1,iVar2);
  return iVar1 == iVar2;
}
