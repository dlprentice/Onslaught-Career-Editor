/* address: 0x0056a8c4 */
/* name: CDXTexture__Unk_0056a8c4 */
/* signature: int __cdecl CDXTexture__Unk_0056a8c4(void * param_1, uint param_2) */


int __cdecl CDXTexture__Unk_0056a8c4(void *param_1,uint param_2)

{
  byte bVar1;
  ushort uVar2;
  byte *pbVar3;
  byte bVar4;
  byte *pbVar5;
  bool bVar6;

  pbVar5 = (byte *)0x0;
  if (DAT_009d33bc == 0) {
    pbVar5 = (byte *)_strrchr(param_1,param_2);
  }
  else {
    CDXTexture__Helper_00561179(0x19);
    do {
      bVar4 = *(byte *)param_1;
      if ((*(byte *)((int)&DAT_009d34c0 + bVar4 + 1) & 4) == 0) {
        bVar6 = param_2 == bVar4;
LAB_0056a91f:
        pbVar3 = param_1;
        if (bVar6) {
          pbVar5 = param_1;
        }
      }
      else {
        bVar1 = *(byte *)((int)param_1 + 1);
        pbVar3 = (byte *)((int)param_1 + 1);
        if (bVar1 == 0) {
          bVar6 = pbVar5 == (byte *)0x0;
          param_1 = pbVar3;
          bVar4 = bVar1;
          goto LAB_0056a91f;
        }
        uVar2 = CONCAT11(bVar4,bVar1);
        bVar4 = bVar1;
        if (param_2 == uVar2) {
          pbVar5 = param_1;
        }
      }
      param_1 = pbVar3 + 1;
    } while (bVar4 != 0);
    CTexture__Helper_005611da(0x19);
  }
  return (int)pbVar5;
}
