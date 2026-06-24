/* address: 0x00564f7a */
/* name: CDXTexture__Helper_00564f7a */
/* signature: int __cdecl CDXTexture__Helper_00564f7a(void * param_1) */


int __cdecl CDXTexture__Helper_00564f7a(void *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;

  iVar2 = 0;
  if ((((byte)*(uint *)((int)param_1 + 0xc) & 3) == 2) &&
     ((*(uint *)((int)param_1 + 0xc) & 0x108) != 0)) {
    iVar3 = *(int *)param_1 - *(int *)((int)param_1 + 8);
    if (0 < iVar3) {
      iVar1 = CTexture__Helper_00567505
                        (*(uint *)((int)param_1 + 0x10),*(int *)((int)param_1 + 8),iVar3);
      if (iVar1 == iVar3) {
        if ((*(uint *)((int)param_1 + 0xc) & 0x80) != 0) {
          *(uint *)((int)param_1 + 0xc) = *(uint *)((int)param_1 + 0xc) & 0xfffffffd;
        }
      }
      else {
        *(uint *)((int)param_1 + 0xc) = *(uint *)((int)param_1 + 0xc) | 0x20;
        iVar2 = -1;
      }
    }
  }
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)param_1 = *(undefined4 *)((int)param_1 + 8);
  return iVar2;
}
