/* address: 0x00465c10 */
/* name: CDXBitmapFont__BuildGlyphRemapTables */
/* signature: void __cdecl CDXBitmapFont__BuildGlyphRemapTables(void) */


void __cdecl CDXBitmapFont__BuildGlyphRemapTables(void)

{
  undefined2 uVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  int iVar5;
  uint uVar6;
  undefined4 *puVar7;
  ushort uVar8;
  byte *pbVar9;
  ushort uVar10;
  uint local_4;

  uVar6 = DAT_005db5fc;
  bVar4 = 0;
  uVar8 = (ushort)DAT_005db5fc;
  uVar2 = DAT_005db5fc;
  uVar10 = uVar8;
  do {
    if (uVar10 == 0) {
LAB_00465c4d:
      bVar4 = 0;
      uVar1 = CONCAT11((char)DAT_00679af4,(char)DAT_00679af4);
      puVar7 = &DAT_006799f4;
      for (iVar5 = 0x40; iVar5 != 0; iVar5 = iVar5 + -1) {
        *puVar7 = CONCAT22(uVar1,uVar1);
        puVar7 = puVar7 + 1;
      }
      puVar7 = &DAT_006799d4;
      for (iVar5 = 8; uVar2 = DAT_005db738, iVar5 != 0; iVar5 = iVar5 + -1) {
        *puVar7 = 0;
        puVar7 = puVar7 + 1;
      }
      if (uVar8 != 0) {
        pbVar9 = (byte *)((int)&DAT_006799d4 + 2);
        do {
          uVar10 = (ushort)uVar2;
          puVar7 = &DAT_005db738;
          uVar8 = (ushort)uVar6;
          uVar3 = uVar2;
          while (uVar10 != 0) {
            if ((ushort)uVar3 == uVar8) goto LAB_00465ccc;
            uVar10 = *(ushort *)((int)puVar7 + 2);
            uVar3 = (uint)uVar10;
            puVar7 = (undefined4 *)((int)puVar7 + 2);
          }
          if (uVar8 < 0x100) {
            *(byte *)((int)&DAT_006799f4 + (uVar6 & 0xffff)) = bVar4;
          }
          else {
            *(ushort *)(pbVar9 + -2) = uVar8;
            *pbVar9 = bVar4;
            pbVar9 = pbVar9 + 4;
          }
LAB_00465ccc:
          bVar4 = bVar4 + 1;
          local_4 = (uint)bVar4;
          uVar10 = *(ushort *)((int)&DAT_005db5fc + local_4 * 2);
          uVar6 = (uint)uVar10;
        } while (uVar10 != 0);
      }
      return;
    }
    if ((short)uVar2 == 0x1f) {
      DAT_00679af4 = CONCAT31(DAT_00679af4._1_3_,bVar4);
      goto LAB_00465c4d;
    }
    bVar4 = bVar4 + 1;
    local_4 = (uint)bVar4;
    uVar10 = *(ushort *)((int)&DAT_005db5fc + local_4 * 2);
    uVar2 = (uint)uVar10;
  } while( true );
}
