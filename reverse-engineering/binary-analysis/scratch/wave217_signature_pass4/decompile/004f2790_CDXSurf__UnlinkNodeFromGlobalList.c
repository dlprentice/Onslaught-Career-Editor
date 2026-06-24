/* address: 0x004f2790 */
/* name: CDXSurf__UnlinkNodeFromGlobalList */
/* signature: void __cdecl CDXSurf__UnlinkNodeFromGlobalList(void * surf_node) */


void __cdecl CDXSurf__UnlinkNodeFromGlobalList(void *surf_node)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int in_ECX;
  int iVar4;

  iVar1 = 0;
  for (iVar2 = DAT_0083d9b0; iVar2 != 0; iVar2 = *(int *)(iVar2 + 0xa0)) {
    if (in_ECX == 0) {
      iVar4 = 0;
    }
    else {
      iVar4 = in_ECX + -8;
    }
    iVar3 = DAT_0083d9b0;
    if ((iVar2 == iVar4) && (iVar3 = *(int *)(iVar2 + 0xa0), iVar1 != 0)) {
      *(int *)(iVar1 + 0xa0) = *(int *)(iVar2 + 0xa0);
      iVar3 = DAT_0083d9b0;
    }
    DAT_0083d9b0 = iVar3;
    iVar1 = iVar2;
  }
  return;
}
