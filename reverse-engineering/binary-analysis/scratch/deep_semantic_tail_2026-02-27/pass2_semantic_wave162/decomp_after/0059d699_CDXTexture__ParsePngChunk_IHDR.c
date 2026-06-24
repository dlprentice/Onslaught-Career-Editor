/* address: 0x0059d699 */
/* name: CDXTexture__ParsePngChunk_IHDR */
/* signature: void __stdcall CDXTexture__ParsePngChunk_IHDR(void * param_1, int param_2, int param_3) */


void CDXTexture__ParsePngChunk_IHDR(void *param_1,int param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  undefined1 local_20 [4];
  undefined1 local_1c [4];
  byte local_18;
  byte local_17;
  byte local_16;
  byte local_15;
  byte local_14;
  uint local_10;
  uint local_c;
  uint local_8;

  if (*(int *)((int)param_1 + 0x58) != 0) {
    CDXTexture__Helper_00592d45(param_1,0x5f3b7c);
  }
  if (param_3 != 0xd) {
    CDXTexture__Helper_00592d45(param_1,0x5f3b68);
  }
  *(uint *)((int)param_1 + 0x58) = *(uint *)((int)param_1 + 0x58) | 1;
  CTexture__Helper_0059cd4b(param_1,(int)local_20,0xd);
  CDXTexture__FinalizePngChunkAndVerifyCrc(param_1,0);
  uVar1 = CDXTexture__ReadU32BigEndian(local_20);
  uVar2 = CDXTexture__ReadU32BigEndian(local_1c);
  local_10 = (uint)local_16;
  local_c = (uint)local_15;
  local_8 = (uint)local_14;
  if ((((uVar1 == 0) || (0x7fffffff < uVar1)) || (uVar2 == 0)) || (0x7fffffff < uVar2)) {
    CDXTexture__Helper_00592d45(param_1,0x5f3b4c);
  }
  if (((local_18 != 1) && (local_18 != 2)) &&
     ((local_18 != 4 && ((local_18 != 8 && (local_18 != 0x10)))))) {
    CDXTexture__Helper_00592d45(param_1,0x5f3b30);
  }
  if (((local_17 == 1) || (local_17 == 5)) || (6 < local_17)) {
    CDXTexture__Helper_00592d45(param_1,0x5f3b14);
  }
  if (((local_17 == 3) && (8 < local_18)) ||
     (((local_17 == 2 || ((local_17 == 4 || (local_17 == 6)))) && (local_18 < 8)))) {
    CDXTexture__Helper_00592d45(param_1,0x5f3ae0);
  }
  if (1 < (int)local_8) {
    CDXTexture__Helper_00592d45(param_1,0x5f3abc);
  }
  if (local_10 != 0) {
    CDXTexture__Helper_00592d45(param_1,0x5f3a98);
  }
  if (local_c != 0) {
    CDXTexture__Helper_00592d45(param_1,0x5f3a78);
  }
  *(undefined1 *)((int)param_1 + 0x113) = (undefined1)local_8;
  *(uint *)((int)param_1 + 0xb8) = uVar1;
  *(uint *)((int)param_1 + 0xbc) = uVar2;
  *(byte *)((int)param_1 + 0x117) = local_18;
  *(byte *)((int)param_1 + 0x116) = local_17;
  if (local_17 != 0) {
    if (local_17 == 2) {
      *(undefined1 *)((int)param_1 + 0x11a) = 3;
      goto LAB_0059d83c;
    }
    if (local_17 != 3) {
      if (local_17 == 4) {
        *(undefined1 *)((int)param_1 + 0x11a) = 2;
      }
      else if (local_17 == 6) {
        *(undefined1 *)((int)param_1 + 0x11a) = 4;
      }
      goto LAB_0059d83c;
    }
  }
  *(undefined1 *)((int)param_1 + 0x11a) = 1;
LAB_0059d83c:
  local_18 = *(char *)((int)param_1 + 0x11a) * local_18;
  *(byte *)((int)param_1 + 0x119) = local_18;
  *(uint *)((int)param_1 + 200) = local_18 * uVar1 + 7 >> 3;
  CTexture__Helper_00594f15();
  return;
}
