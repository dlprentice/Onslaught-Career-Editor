/* address: 0x0044c780 */
/* name: OID__Helper_0044c780 */
/* signature: int __thiscall OID__Helper_0044c780(void * this, int param_1, float param_2, float param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall
OID__Helper_0044c780(void *this,int param_1,float param_2,float param_3,float param_4)

{
  int iVar1;
  int iVar2;
  double dVar3;
  int local_8;

  dVar3 = CHeightField__Unk_0047eb80(0x6fadc8,&param_1);
  if ((double)_DAT_005db2b0 < (double)param_3 - dVar3) {
    local_8 = (int)(longlong)ROUND((float)param_1);
    iVar1 = local_8 + (local_8 >> 0x1f & 7U);
    local_8 = (int)(longlong)ROUND(param_2);
    iVar1 = iVar1 >> 3;
    iVar2 = (int)(local_8 + (local_8 >> 0x1f & 7U)) >> 3;
    if ((((-1 < iVar1) && (-1 < iVar2)) && (iVar1 < 0x40)) && (iVar2 < 0x40)) {
      return *(int *)((int)this + (iVar1 * 0x40 + iVar2) * 4 + 0x4008);
    }
  }
  return 1;
}
