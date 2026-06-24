/* address: 0x005933c6 */
/* name: CDXTexture__DecodePngRowsAcrossPasses */
/* signature: void __stdcall CDXTexture__DecodePngRowsAcrossPasses(int param_1, void * param_2) */


void CDXTexture__DecodePngRowsAcrossPasses(int param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  undefined4 local_8;

  local_8 = CDXTexture__GetPngPassCountFromInterlace(param_1);
  iVar1 = *(int *)(param_1 + 0xbc);
  *(int *)(param_1 + 0xc0) = iVar1;
  iVar2 = iVar1;
  piVar3 = param_2;
  if (0 < local_8) {
    do {
      for (; iVar2 != 0; iVar2 = iVar2 + -1) {
        CDXTexture__Helper_00593043((void *)param_1,*piVar3,0);
        piVar3 = piVar3 + 1;
      }
      local_8 = local_8 + -1;
      iVar2 = iVar1;
      piVar3 = param_2;
    } while (local_8 != 0);
  }
  return;
}
