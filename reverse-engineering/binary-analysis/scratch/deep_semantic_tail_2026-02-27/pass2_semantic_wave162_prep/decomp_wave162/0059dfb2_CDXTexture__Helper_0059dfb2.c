/* address: 0x0059dfb2 */
/* name: CDXTexture__Helper_0059dfb2 */
/* signature: uint __stdcall CDXTexture__Helper_0059dfb2(uint param_1, void * param_2, uint param_3) */


uint CDXTexture__Helper_0059dfb2(uint param_1,void *param_2,uint param_3)

{
  uint uVar1;
  uint uVar2;

  if (param_2 == (void *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = ~param_1;
    if (7 < param_3) {
      uVar2 = param_3 >> 3;
      do {
        param_3 = param_3 - 8;
        uVar1 = uVar1 >> 8 ^ *(uint *)(&DAT_005f3ec0 + ((*(byte *)param_2 ^ uVar1) & 0xff) * 4);
        uVar1 = uVar1 >> 8 ^
                *(uint *)(&DAT_005f3ec0 + ((*(byte *)((int)param_2 + 1) ^ uVar1) & 0xff) * 4);
        uVar1 = uVar1 >> 8 ^
                *(uint *)(&DAT_005f3ec0 + ((*(byte *)((int)param_2 + 2) ^ uVar1) & 0xff) * 4);
        uVar1 = uVar1 >> 8 ^
                *(uint *)(&DAT_005f3ec0 + ((*(byte *)((int)param_2 + 3) ^ uVar1) & 0xff) * 4);
        uVar1 = uVar1 >> 8 ^
                *(uint *)(&DAT_005f3ec0 + ((*(byte *)((int)param_2 + 4) ^ uVar1) & 0xff) * 4);
        uVar1 = uVar1 >> 8 ^
                *(uint *)(&DAT_005f3ec0 + ((*(byte *)((int)param_2 + 5) ^ uVar1) & 0xff) * 4);
        uVar1 = uVar1 >> 8 ^
                *(uint *)(&DAT_005f3ec0 + ((*(byte *)((int)param_2 + 6) ^ uVar1) & 0xff) * 4);
        uVar1 = uVar1 >> 8 ^
                *(uint *)(&DAT_005f3ec0 + ((*(byte *)((int)param_2 + 7) ^ uVar1) & 0xff) * 4);
        param_2 = (void *)((int)param_2 + 8);
        uVar2 = uVar2 - 1;
      } while (uVar2 != 0);
    }
    for (; param_3 != 0; param_3 = param_3 - 1) {
      uVar1 = uVar1 >> 8 ^ *(uint *)(&DAT_005f3ec0 + ((*(byte *)param_2 ^ uVar1) & 0xff) * 4);
      param_2 = (void *)((int)param_2 + 1);
    }
    uVar1 = ~uVar1;
  }
  return uVar1;
}
