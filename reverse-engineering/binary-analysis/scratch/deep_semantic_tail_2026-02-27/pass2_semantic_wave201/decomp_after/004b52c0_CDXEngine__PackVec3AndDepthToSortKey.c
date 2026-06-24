/* address: 0x004b52c0 */
/* name: CDXEngine__PackVec3AndDepthToSortKey */
/* signature: int __cdecl CDXEngine__PackVec3AndDepthToSortKey(void * param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CDXEngine__PackVec3AndDepthToSortKey(void *param_1,float param_2)

{
  int iVar1;
  int iVar2;
  undefined4 local_8;

  local_8 = (int)(longlong)ROUND(*(float *)param_1 * _DAT_005dbc4c + _DAT_005d95b8);
  iVar1 = local_8;
  local_8 = (int)(longlong)ROUND(param_2 * _DAT_005d9644);
  iVar2 = local_8 * -0x100;
  local_8 = (int)(longlong)ROUND(*(float *)((int)param_1 + 4) * _DAT_005dbc4c + _DAT_005d95b8);
  iVar2 = (iVar1 + iVar2) * 0x100 + local_8;
  local_8 = (int)(longlong)ROUND(*(float *)((int)param_1 + 8) * _DAT_005dbc4c + _DAT_005d95b8);
  return iVar2 * 0x100 + local_8;
}
