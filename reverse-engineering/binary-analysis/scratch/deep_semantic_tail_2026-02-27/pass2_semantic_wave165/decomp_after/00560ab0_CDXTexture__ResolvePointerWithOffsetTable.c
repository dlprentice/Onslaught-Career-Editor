/* address: 0x00560ab0 */
/* name: CDXTexture__ResolvePointerWithOffsetTable */
/* signature: int __cdecl CDXTexture__ResolvePointerWithOffsetTable(int param_1, void * param_2) */


int __cdecl CDXTexture__ResolvePointerWithOffsetTable(int param_1,void *param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = *(int *)((int)param_2 + 4);
  iVar2 = *(int *)param_2 + param_1;
  if (-1 < iVar1) {
    iVar2 = iVar2 + *(int *)(*(int *)(iVar1 + param_1) + *(int *)((int)param_2 + 8)) + iVar1;
  }
  return iVar2;
}
