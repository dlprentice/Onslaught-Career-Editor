/* address: 0x00569f92 */
/* name: CDXTexture__Helper_00569f92 */
/* signature: uint __cdecl CDXTexture__Helper_00569f92(int param_1, void * param_2, uint param_3) */


uint __cdecl CDXTexture__Helper_00569f92(int param_1,void *param_2,uint param_3)

{
  byte bVar1;
  int iVar2;
  undefined4 *puVar3;

  if ((param_2 != (void *)0x0) && (param_3 != 0)) {
    bVar1 = *(byte *)param_2;
    if (bVar1 != 0) {
      if (DAT_009d0998 == 0) {
        if (param_1 != 0) {
          *(ushort *)param_1 = (ushort)bVar1;
        }
        return 1;
      }
      if ((PTR_DAT_00653890[(uint)bVar1 * 2 + 1] & 0x80) == 0) {
        iVar2 = MultiByteToWideChar(DAT_009d09a8,9,param_2,1,(LPWSTR)param_1,(uint)(param_1 != 0));
        if (iVar2 != 0) {
          return 1;
        }
      }
      else {
        if (1 < (int)DAT_00653a9c) {
          if ((int)param_3 < (int)DAT_00653a9c) goto LAB_0056a024;
          iVar2 = MultiByteToWideChar(DAT_009d09a8,9,param_2,DAT_00653a9c,(LPWSTR)param_1,
                                      (uint)(param_1 != 0));
          if (iVar2 != 0) {
            return DAT_00653a9c;
          }
        }
        if ((DAT_00653a9c <= param_3) && (*(char *)((int)param_2 + 1) != '\0')) {
          return DAT_00653a9c;
        }
      }
LAB_0056a024:
      puVar3 = (undefined4 *)CTexture__Helper_00567aa8();
      *puVar3 = 0x2a;
      return 0xffffffff;
    }
    if (param_1 != 0) {
      *(undefined2 *)param_1 = 0;
    }
  }
  return 0;
}
