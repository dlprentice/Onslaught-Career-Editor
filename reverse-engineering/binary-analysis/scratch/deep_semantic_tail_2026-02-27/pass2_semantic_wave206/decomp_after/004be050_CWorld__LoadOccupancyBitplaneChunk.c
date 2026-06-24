/* address: 0x004be050 */
/* name: CWorld__LoadOccupancyBitplaneChunk */
/* signature: void __fastcall CWorld__LoadOccupancyBitplaneChunk(int param_1) */


void __fastcall CWorld__LoadOccupancyBitplaneChunk(int param_1)

{
  int iVar1;
  byte *pbVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_c;
  int local_8;
  uint local_4;

  DXMemBuffer__ReadBytes(&local_8,4);
  if (local_8 == 1) {
    local_c = 0;
    do {
      iVar4 = local_c >> 1;
      iVar5 = 0;
      do {
        DXMemBuffer__ReadBytes(&local_4,1);
        iVar6 = 0;
        do {
          uVar3 = iVar5 + iVar6 >> 1;
          if ((((-1 < (int)uVar3) && ((int)uVar3 < 0x100)) && (-1 < iVar4)) && (iVar4 < 0x100)) {
            iVar1 = iVar5 + iVar6 >> 4;
            if (((local_4 & 0xff) >> ((byte)iVar6 & 0x1f) & 1) == 0) {
              pbVar2 = (byte *)(iVar1 * 0x100 + iVar4 + param_1);
              uVar3 = uVar3 & 0x80000007;
              if ((int)uVar3 < 0) {
                uVar3 = (uVar3 - 1 | 0xfffffff8) + 1;
              }
              *pbVar2 = *pbVar2 & -('\x01' << ((byte)uVar3 & 0x1f)) - 1U;
            }
            else {
              pbVar2 = (byte *)(iVar1 * 0x100 + iVar4 + param_1);
              uVar3 = uVar3 & 0x80000007;
              if ((int)uVar3 < 0) {
                uVar3 = (uVar3 - 1 | 0xfffffff8) + 1;
              }
              *pbVar2 = *pbVar2 | '\x01' << ((byte)uVar3 & 0x1f);
            }
          }
          iVar6 = iVar6 + 1;
        } while (iVar6 < 8);
        iVar5 = iVar5 + 8;
      } while (iVar5 < 0x200);
      local_c = local_c + 1;
    } while (local_c < 0x200);
  }
  else if (local_8 == 2) {
    iVar4 = 0;
    do {
      iVar5 = iVar4 + param_1;
      iVar6 = 0x20;
      do {
        DXMemBuffer__ReadBytes(iVar5,1);
        iVar5 = iVar5 + 0x100;
        iVar6 = iVar6 + -1;
      } while (iVar6 != 0);
      iVar4 = iVar4 + 1;
    } while (iVar4 < 0x100);
    return;
  }
  return;
}
