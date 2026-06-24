/* address: 0x0056a82d */
/* name: CDXTexture__Unk_0056a82d */
/* signature: int __cdecl CDXTexture__Unk_0056a82d(void * param_1, uint param_2) */


int __cdecl CDXTexture__Unk_0056a82d(void *param_1,uint param_2)

{
  byte bVar1;
  char *pcVar2;
  uint uVar3;
  byte *pbVar4;

  if (DAT_009d33bc == 0) {
    pcVar2 = _strchr(param_1,param_2);
  }
  else {
    CDXTexture__Helper_00561179(0x19);
    while( true ) {
      bVar1 = *(byte *)param_1;
      uVar3 = (uint)bVar1;
      if (bVar1 == 0) break;
      if ((*(byte *)((int)&DAT_009d34c0 + uVar3 + 1) & 4) == 0) {
        pbVar4 = param_1;
        if (param_2 == uVar3) break;
      }
      else {
        pbVar4 = (byte *)((int)param_1 + 1);
        if (*(byte *)((int)param_1 + 1) == 0) {
          CTexture__Helper_005611da(0x19);
          return 0;
        }
        if (param_2 == CONCAT11(bVar1,*(byte *)((int)param_1 + 1))) {
          CTexture__Helper_005611da(0x19);
          return (int)param_1;
        }
      }
      param_1 = pbVar4 + 1;
    }
    CTexture__Helper_005611da(0x19);
    pcVar2 = (char *)(~-(uint)(param_2 != uVar3) & (uint)param_1);
  }
  return (int)pcVar2;
}
