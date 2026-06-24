/* address: 0x005aefa0 */
/* name: CDXTexture__Unk_005aefa0 */
/* signature: void __fastcall CDXTexture__Unk_005aefa0(int param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXTexture__Unk_005aefa0(int param_1,int param_2,int param_3,void *param_4)

{
  undefined8 uVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  int iVar9;
  ulonglong uVar10;
  ulonglong uVar11;
  ulonglong uVar12;
  ulonglong uVar13;
  ulonglong uVar14;
  ulonglong uVar15;
  int *in_EAX;
  undefined8 *puVar16;
  undefined8 *puVar17;
  ulonglong *puVar18;
  int iVar19;
  ulonglong *puVar20;
  ulonglong *puVar21;
  undefined8 *puVar22;
  undefined8 *puVar23;
  undefined1 uVar30;
  short sVar24;
  short sVar25;
  ushort uVar26;
  short sVar27;
  undefined1 uVar31;
  undefined1 uVar33;
  short sVar32;
  short sVar34;
  char cVar35;
  char cVar36;
  short sVar37;
  byte bVar39;
  short sVar38;
  short sVar40;
  short sVar41;
  short sVar44;
  undefined4 uVar42;
  short sVar45;
  short sVar46;
  short sVar47;
  undefined1 uVar52;
  short sVar48;
  short sVar49;
  undefined1 uVar53;
  undefined1 uVar55;
  short sVar54;
  short sVar56;
  short sVar57;
  char cVar58;
  undefined6 uVar50;
  char cVar59;
  short sVar60;
  byte bVar61;
  undefined4 uVar62;
  undefined4 uVar63;
  undefined6 uVar64;
  ulonglong uVar66;
  ulonglong uVar67;
  undefined4 uVar28;
  undefined6 uVar29;
  undefined6 uVar43;
  undefined8 uVar51;
  undefined6 uVar65;

  iVar2 = *in_EAX;
  iVar3 = *(int *)(param_2 + 0x28);
  iVar19 = 0;
  if (0 < *(int *)(param_3 + 0x13c)) {
    do {
      puVar18 = *(ulonglong **)param_4;
      puVar20 = *(ulonglong **)((int)param_4 + -4);
      puVar21 = *(ulonglong **)((int)param_4 + 4);
      puVar22 = *(undefined8 **)(iVar2 + iVar19 * 4);
      puVar23 = *(undefined8 **)(iVar2 + 4 + iVar19 * 4);
      puVar17 = (undefined8 *)((int)puVar22 + iVar3 * 4);
      iVar19 = iVar19 + 2;
      uVar66 = *puVar18;
      uVar67 = *puVar20;
      uVar7 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x18);
      uVar33 = (undefined1)(uVar66 >> 0x18);
      sVar4 = CONCAT11(uVar7,uVar33);
      uVar6 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x10);
      uVar31 = (undefined1)(uVar66 >> 0x10);
      uVar5 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 8);
      uVar30 = (undefined1)(uVar66 >> 8);
      sVar32 = CONCAT11(uVar5,uVar30);
      sVar34 = CONCAT11((char)(undefined4)DAT_005f4a20,(char)uVar66);
      sVar24 = sVar34 * (short)DAT_005f49e0;
      sVar37 = (short)CONCAT31(CONCAT21(sVar4,uVar6),uVar31);
      uVar55 = (undefined1)(uVar67 >> 0x18);
      sVar38 = CONCAT11(uVar7,uVar55);
      uVar53 = (undefined1)(uVar67 >> 0x10);
      uVar52 = (undefined1)(uVar67 >> 8);
      sVar40 = CONCAT11(uVar5,uVar52);
      sVar49 = CONCAT11((char)(undefined4)DAT_005f4a20,(char)uVar67);
      sVar41 = (short)DAT_005f49e8;
      uVar10 = (ulonglong)DAT_005f49e8 >> 0x10;
      uVar11 = (ulonglong)DAT_005f49e8 >> 0x20;
      sVar56 = (short)CONCAT31(CONCAT21(sVar38,uVar6),uVar53);
      uVar12 = (ulonglong)DAT_005f49e8 >> 0x30;
      sVar44 = sVar34 * (short)((ulonglong)DAT_005f49d0 >> 0x10) +
               sVar32 * (short)((ulonglong)DAT_005f49e0 >> 0x10);
      sVar45 = sVar32 * (short)((ulonglong)DAT_005f49d0 >> 0x20) +
               sVar37 * (short)((ulonglong)DAT_005f49e0 >> 0x20);
      sVar46 = sVar37 * (short)((ulonglong)DAT_005f49d0 >> 0x30) +
               sVar4 * (short)((ulonglong)DAT_005f49e0 >> 0x30);
      *puVar17 = CONCAT26(sVar46,CONCAT24(sVar45,CONCAT22(sVar44,sVar24)));
      sVar4 = (short)DAT_005f49f8;
      uVar13 = (ulonglong)DAT_005f49f8 >> 0x10;
      uVar14 = (ulonglong)DAT_005f49f8 >> 0x20;
      uVar15 = (ulonglong)DAT_005f49f8 >> 0x30;
      uVar8 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x18);
      uVar7 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x10);
      uVar6 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 8);
      uVar5 = (undefined1)(undefined4)DAT_005f4a20;
      sVar47 = CONCAT11(uVar8,(char)(uVar66 >> 0x20));
      sVar32 = (short)((ulonglong)DAT_005f49d0 >> 0x10);
      sVar34 = (short)((ulonglong)DAT_005f49d0 >> 0x20);
      sVar37 = (short)((ulonglong)DAT_005f49d0 >> 0x30);
      sVar27 = CONCAT11(uVar8,(char)(uVar67 >> 0x20));
      sVar48 = CONCAT11(uVar5,(char)uVar67) * (short)DAT_005f49d0;
      sVar54 = CONCAT11(uVar6,uVar52) * sVar32;
      sVar57 = (short)CONCAT31(CONCAT21(CONCAT11(uVar8,uVar55),uVar7),uVar53) * sVar34;
      sVar60 = CONCAT11(uVar8,uVar55) * sVar37;
      uVar51 = CONCAT26(sVar60,CONCAT24(sVar57,CONCAT22(sVar54,sVar48)));
      sVar25 = CONCAT11(uVar5,(char)uVar66) * (short)DAT_005f49d8 +
               CONCAT11(uVar5,uVar30) * (short)DAT_005f49d0;
      sVar32 = CONCAT11(uVar6,uVar30) * (short)((ulonglong)DAT_005f49d8 >> 0x10) +
               CONCAT11(uVar6,uVar31) * sVar32;
      sVar34 = (short)CONCAT31(CONCAT21(CONCAT11(uVar8,uVar33),uVar7),uVar31) *
               (short)((ulonglong)DAT_005f49d8 >> 0x20) +
               (short)CONCAT31(CONCAT21(sVar47,uVar7),uVar33) * sVar34;
      sVar37 = CONCAT11(uVar8,uVar33) * (short)((ulonglong)DAT_005f49d8 >> 0x30) + sVar47 * sVar37;
      puVar17[1] = CONCAT26(sVar37,CONCAT24(sVar34,CONCAT22(sVar32,sVar25)));
      uVar26 = (ushort)(sVar25 + CONCAT11(uVar5,uVar52) + (short)DAT_005f49f0 + sVar48) >> 4;
      uVar28 = CONCAT22((ushort)(sVar32 + CONCAT11(uVar6,uVar53) +
                                 (short)((ulonglong)DAT_005f49f0 >> 0x10) + sVar54) >> 4,uVar26);
      uVar29 = CONCAT24((ushort)(sVar34 + (short)CONCAT31(CONCAT21(sVar27,uVar7),uVar55) +
                                 (short)((ulonglong)DAT_005f49f0 >> 0x20) + sVar57) >> 4,uVar28);
      *puVar22 = CONCAT26(((ushort)(sVar46 + sVar56 + sVar38 * (short)uVar12 + (short)uVar15) >> 4)
                          + (short)(CONCAT26((ushort)(sVar37 + sVar27 +
                                                      (short)((ulonglong)DAT_005f49f0 >> 0x30) +
                                                     sVar60) >> 4,uVar29) >> 0x28),
                          CONCAT24(((ushort)(sVar45 + sVar40 + sVar56 * (short)uVar11 +
                                            (short)uVar14) >> 4) + (short)((uint6)uVar29 >> 0x18),
                                   CONCAT22(((ushort)(sVar44 + sVar49 + sVar40 * (short)uVar10 +
                                                     (short)uVar13) >> 4) +
                                            (short)((uint)uVar28 >> 8),
                                            ((ushort)(sVar24 + sVar49 * sVar41 + sVar4) >> 4) +
                                            uVar26 * 0x100)));
      puVar22 = puVar22 + 1;
      puVar16 = puVar17 + 2;
      iVar9 = iVar3;
      while( true ) {
        iVar9 = iVar9 + -8;
        uVar5 = (undefined1)DAT_005f4a20._4_4_;
        uVar6 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 8);
        uVar7 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x10);
        uVar8 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x18);
        uVar31 = (undefined1)(uVar66 >> 0x18);
        uVar30 = (undefined1)(uVar66 >> 0x20);
        cVar35 = (char)(uVar66 >> 0x28);
        cVar36 = (char)(uVar66 >> 0x30);
        bVar39 = (byte)(uVar66 >> 0x38);
        sVar32 = (short)((ulonglong)DAT_005f49d8 >> 0x10);
        sVar34 = (short)((ulonglong)DAT_005f49d8 >> 0x20);
        sVar38 = (short)((ulonglong)DAT_005f49d8 >> 0x30);
        sVar4 = (short)DAT_005f49d0;
        sVar41 = (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar37 = (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar47 = (short)((ulonglong)DAT_005f49d0 >> 0x30);
        uVar52 = (undefined1)(uVar67 >> 0x18);
        uVar33 = (undefined1)(uVar67 >> 0x20);
        cVar58 = (char)(uVar67 >> 0x28);
        cVar59 = (char)(uVar67 >> 0x30);
        bVar61 = (byte)(uVar67 >> 0x38);
        if (iVar9 < 1) break;
        uVar28 = CONCAT13(uVar6,CONCAT12(cVar35,CONCAT11(uVar5,uVar30)));
        uVar29 = CONCAT15(uVar7,CONCAT14(cVar36,uVar28));
        sVar40 = CONCAT11(uVar5,uVar31);
        uVar42 = CONCAT13(uVar6,CONCAT12(uVar30,sVar40));
        uVar43 = CONCAT15(uVar7,CONCAT14(cVar35,uVar42));
        sVar27 = CONCAT11(uVar5,uVar30) * (short)DAT_005f49d8;
        sVar32 = (short)((uint)uVar28 >> 0x10) * sVar32;
        sVar34 = (short)((uint6)uVar29 >> 0x20) * sVar34;
        sVar38 = (short)(CONCAT17(uVar8,CONCAT16(bVar39,uVar29)) >> 0x30) * sVar38;
        uVar28 = CONCAT13(uVar6,CONCAT12(cVar58,CONCAT11(uVar5,uVar33)));
        uVar29 = CONCAT15(uVar7,CONCAT14(cVar59,uVar28));
        sVar49 = CONCAT11(uVar5,uVar52);
        uVar62 = CONCAT13(uVar6,CONCAT12(uVar33,sVar49));
        uVar50 = CONCAT15(uVar7,CONCAT14(cVar58,uVar62));
        sVar25 = CONCAT11(uVar5,uVar33) * sVar4;
        sVar44 = (short)((uint)uVar28 >> 0x10) * sVar41;
        sVar45 = (short)((uint6)uVar29 >> 0x20) * sVar37;
        sVar46 = (short)(CONCAT17(uVar8,CONCAT16(bVar61,uVar29)) >> 0x30) * sVar47;
        sVar40 = sVar40 * sVar4 + sVar27;
        sVar24 = (short)((uint)uVar42 >> 0x10) * sVar41 + sVar32;
        sVar37 = (short)((uint6)uVar43 >> 0x20) * sVar37 + sVar34;
        sVar47 = (short)(CONCAT17(uVar8,CONCAT16(cVar36,uVar43)) >> 0x30) * sVar47 + sVar38;
        *puVar16 = CONCAT26(sVar47,CONCAT24(sVar37,CONCAT22(sVar24,sVar40)));
        sVar4 = (short)DAT_005f49f8;
        uVar10 = (ulonglong)DAT_005f49f8 >> 0x10;
        uVar11 = (ulonglong)DAT_005f49f8 >> 0x20;
        uVar12 = (ulonglong)DAT_005f49f8 >> 0x30;
        uVar66 = puVar18[1];
        sVar41 = CONCAT11((char)DAT_005f4a20._4_4_,cVar35);
        uVar5 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 8);
        uVar28 = CONCAT13(uVar5,CONCAT12(cVar36,sVar41));
        uVar6 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x10);
        uVar29 = CONCAT15(uVar6,CONCAT14(bVar39,uVar28));
        uVar7 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x18);
        uVar67 = puVar20[1];
        sVar48 = CONCAT11((char)DAT_005f4a20._4_4_,cVar58);
        uVar42 = CONCAT13(uVar5,CONCAT12(cVar59,sVar48));
        uVar43 = CONCAT15(uVar6,CONCAT14(bVar61,uVar42));
        sVar27 = sVar27 + sVar41 * (short)DAT_005f49d0;
        sVar32 = sVar32 + (short)((uint)uVar28 >> 0x10) * (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar34 = sVar34 + (short)((uint6)uVar29 >> 0x20) * (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar38 = sVar38 + (short)(CONCAT17(uVar7,CONCAT16((char)uVar66,uVar29)) >> 0x30) *
                          (short)((ulonglong)DAT_005f49d0 >> 0x30);
        puVar16[1] = CONCAT26(sVar38,CONCAT24(sVar34,CONCAT22(sVar32,sVar27)));
        uVar26 = (ushort)(sVar27 + sVar48 + (short)DAT_005f49f0 + sVar25) >> 4;
        uVar28 = CONCAT22((ushort)(sVar32 + (short)((uint)uVar42 >> 0x10) +
                                            (short)((ulonglong)DAT_005f49f0 >> 0x10) + sVar44) >> 4,
                          uVar26);
        uVar29 = CONCAT24((ushort)(sVar34 + (short)((uint6)uVar43 >> 0x20) +
                                            (short)((ulonglong)DAT_005f49f0 >> 0x20) + sVar45) >> 4,
                          uVar28);
        *puVar22 = CONCAT26(((ushort)(sVar47 + (short)uVar12 +
                                     (short)(CONCAT17(uVar8,CONCAT16(cVar59,uVar50)) >> 0x30) +
                                     sVar46) >> 4) +
                            (short)(CONCAT26((ushort)(sVar38 + (short)(CONCAT17(uVar7,CONCAT16((char
                                                  )uVar67,uVar43)) >> 0x30) +
                                                  (short)((ulonglong)DAT_005f49f0 >> 0x30) + sVar46)
                                             >> 4,uVar29) >> 0x28),
                            CONCAT24(((ushort)(sVar37 + (short)uVar11 +
                                              (short)((uint6)uVar50 >> 0x20) + sVar45) >> 4) +
                                     (short)((uint6)uVar29 >> 0x18),
                                     CONCAT22(((ushort)(sVar24 + (short)uVar10 +
                                                       (short)((uint)uVar62 >> 0x10) + sVar44) >> 4)
                                              + (short)((uint)uVar28 >> 8),
                                              ((ushort)(sVar40 + sVar4 + sVar49 + sVar25) >> 4) +
                                              uVar26 * 0x100)));
        uVar7 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x18);
        uVar33 = (undefined1)(uVar66 >> 0x18);
        sVar34 = CONCAT11(uVar7,uVar33);
        uVar6 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x10);
        uVar31 = (undefined1)(uVar66 >> 0x10);
        uVar5 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 8);
        uVar30 = (undefined1)(uVar66 >> 8);
        sVar38 = CONCAT11(uVar5,uVar30);
        sVar27 = CONCAT11((char)(undefined4)DAT_005f4a20,(char)uVar66);
        sVar45 = (short)CONCAT31(CONCAT21(sVar34,uVar6),uVar31);
        sVar40 = sVar27 * (short)DAT_005f49d8;
        sVar24 = sVar38 * (short)((ulonglong)DAT_005f49d8 >> 0x10);
        sVar25 = sVar45 * (short)((ulonglong)DAT_005f49d8 >> 0x20);
        sVar34 = sVar34 * (short)((ulonglong)DAT_005f49d8 >> 0x30);
        sVar4 = (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar41 = (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar32 = (short)((ulonglong)DAT_005f49d0 >> 0x30);
        uVar55 = (undefined1)(uVar67 >> 0x18);
        sVar37 = CONCAT11(uVar7,uVar55);
        uVar53 = (undefined1)(uVar67 >> 0x10);
        uVar52 = (undefined1)(uVar67 >> 8);
        sVar47 = CONCAT11(uVar5,uVar52);
        sVar46 = CONCAT11((char)(undefined4)DAT_005f4a20,(char)uVar67);
        sVar56 = (short)CONCAT31(CONCAT21(sVar37,uVar6),uVar53);
        sVar49 = sVar46 * (short)DAT_005f49d0;
        sVar48 = sVar47 * sVar4;
        sVar54 = sVar56 * sVar41;
        sVar37 = sVar37 * sVar32;
        uVar51 = CONCAT26(sVar37,CONCAT24(sVar54,CONCAT22(sVar48,sVar49)));
        sVar44 = (ushort)bVar39 * (short)DAT_005f49d0 + sVar40;
        sVar27 = sVar27 * sVar4 + sVar24;
        sVar38 = sVar38 * sVar41 + sVar25;
        sVar45 = sVar45 * sVar32 + sVar34;
        puVar16[2] = CONCAT26(sVar45,CONCAT24(sVar38,CONCAT22(sVar27,sVar44)));
        sVar4 = (short)DAT_005f49f8;
        uVar10 = (ulonglong)DAT_005f49f8 >> 0x10;
        uVar11 = (ulonglong)DAT_005f49f8 >> 0x20;
        uVar12 = (ulonglong)DAT_005f49f8 >> 0x30;
        uVar8 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x18);
        sVar41 = CONCAT11(uVar8,(char)(uVar66 >> 0x20));
        uVar7 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x10);
        uVar6 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 8);
        uVar5 = (undefined1)(undefined4)DAT_005f4a20;
        sVar32 = CONCAT11(uVar8,(char)(uVar67 >> 0x20));
        sVar40 = sVar40 + CONCAT11(uVar5,uVar30) * (short)DAT_005f49d0;
        sVar24 = sVar24 + CONCAT11(uVar6,uVar31) * (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar25 = sVar25 + (short)CONCAT31(CONCAT21(sVar41,uVar7),uVar33) *
                          (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar34 = sVar34 + sVar41 * (short)((ulonglong)DAT_005f49d0 >> 0x30);
        puVar16[3] = CONCAT26(sVar34,CONCAT24(sVar25,CONCAT22(sVar24,sVar40)));
        uVar26 = (ushort)(sVar40 + CONCAT11(uVar5,uVar52) + (short)DAT_005f49f0 + sVar49) >> 4;
        uVar28 = CONCAT22((ushort)(sVar24 + CONCAT11(uVar6,uVar53) +
                                   (short)((ulonglong)DAT_005f49f0 >> 0x10) + sVar48) >> 4,uVar26);
        uVar29 = CONCAT24((ushort)(sVar25 + (short)CONCAT31(CONCAT21(sVar32,uVar7),uVar55) +
                                   (short)((ulonglong)DAT_005f49f0 >> 0x20) + sVar54) >> 4,uVar28);
        puVar22[1] = CONCAT26(((ushort)(sVar45 + (short)uVar12 + sVar56 + sVar37) >> 4) +
                              (short)(CONCAT26((ushort)(sVar34 + sVar32 +
                                                        (short)((ulonglong)DAT_005f49f0 >> 0x30) +
                                                       sVar37) >> 4,uVar29) >> 0x28),
                              CONCAT24(((ushort)(sVar38 + (short)uVar11 + sVar47 + sVar54) >> 4) +
                                       (short)((uint6)uVar29 >> 0x18),
                                       CONCAT22(((ushort)(sVar27 + (short)uVar10 + sVar46 + sVar48)
                                                >> 4) + (short)((uint)uVar28 >> 8),
                                                ((ushort)(sVar44 + sVar4 + (ushort)bVar61 + sVar49)
                                                >> 4) + uVar26 * 0x100)));
        puVar22 = puVar22 + 2;
        puVar18 = puVar18 + 1;
        puVar20 = puVar20 + 1;
        puVar16 = puVar16 + 4;
      }
      uVar28 = CONCAT13(uVar6,CONCAT12(cVar35,CONCAT11(uVar5,uVar30)));
      uVar29 = CONCAT15(uVar7,CONCAT14(cVar36,uVar28));
      sVar40 = CONCAT11(uVar5,uVar31);
      uVar42 = CONCAT13(uVar6,CONCAT12(uVar30,sVar40));
      uVar43 = CONCAT15(uVar7,CONCAT14(cVar35,uVar42));
      sVar27 = CONCAT11(uVar5,uVar30) * (short)DAT_005f49d8;
      sVar32 = (short)((uint)uVar28 >> 0x10) * sVar32;
      sVar34 = (short)((uint6)uVar29 >> 0x20) * sVar34;
      sVar38 = (short)(CONCAT17(uVar8,CONCAT16(bVar39,uVar29)) >> 0x30) * sVar38;
      sVar46 = CONCAT11(uVar5,uVar52);
      uVar62 = CONCAT13(uVar6,CONCAT12(uVar33,sVar46));
      uVar50 = CONCAT15(uVar7,CONCAT14(cVar58,uVar62));
      sVar40 = sVar40 * sVar4 + sVar27;
      sVar24 = (short)((uint)uVar42 >> 0x10) * sVar41 + sVar32;
      sVar37 = (short)((uint6)uVar43 >> 0x20) * sVar37 + sVar34;
      sVar47 = (short)(CONCAT17(uVar8,CONCAT16(cVar36,uVar43)) >> 0x30) * sVar47 + sVar38;
      *puVar16 = CONCAT26(sVar47,CONCAT24(sVar37,CONCAT22(sVar24,sVar40)));
      sVar4 = (short)DAT_005f49f8;
      uVar10 = (ulonglong)DAT_005f49f8 >> 0x10;
      uVar11 = (ulonglong)DAT_005f49f8 >> 0x20;
      uVar12 = (ulonglong)DAT_005f49f8 >> 0x30;
      sVar25 = (short)((ulonglong)uVar51 >> 0x10);
      sVar44 = (short)((ulonglong)uVar51 >> 0x20);
      sVar45 = (short)((ulonglong)uVar51 >> 0x30);
      uVar66 = uVar66 & _DAT_005f4a10;
      sVar41 = CONCAT11((char)DAT_005f4a20._4_4_,cVar35 + (char)(uVar66 >> 0x20));
      uVar5 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 8);
      uVar28 = CONCAT13(uVar5,CONCAT12(cVar36 + (char)(uVar66 >> 0x28),sVar41));
      uVar6 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x10);
      uVar29 = CONCAT15(uVar6,CONCAT14(bVar39 + (char)(uVar66 >> 0x30),uVar28));
      uVar7 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x18);
      uVar67 = uVar67 & _DAT_005f4a10;
      sVar49 = CONCAT11((char)DAT_005f4a20._4_4_,cVar58 + (char)(uVar67 >> 0x20));
      uVar42 = CONCAT13(uVar5,CONCAT12(cVar59 + (char)(uVar67 >> 0x28),sVar49));
      uVar43 = CONCAT15(uVar6,CONCAT14(bVar61 + (char)(uVar67 >> 0x30),uVar42));
      sVar27 = sVar27 + sVar41 * (short)DAT_005f49d0;
      sVar32 = sVar32 + (short)((uint)uVar28 >> 0x10) * (short)((ulonglong)DAT_005f49d0 >> 0x10);
      sVar34 = sVar34 + (short)((uint6)uVar29 >> 0x20) * (short)((ulonglong)DAT_005f49d0 >> 0x20);
      sVar38 = sVar38 + (short)(CONCAT17(uVar7,CONCAT16((char)(uVar66 >> 0x38),uVar29)) >> 0x30) *
                        (short)((ulonglong)DAT_005f49d0 >> 0x30);
      puVar16[1] = CONCAT26(sVar38,CONCAT24(sVar34,CONCAT22(sVar32,sVar27)));
      uVar26 = (ushort)(sVar27 + sVar49 + (short)DAT_005f49f0 + (short)uVar51) >> 4;
      uVar28 = CONCAT22((ushort)(sVar32 + (short)((uint)uVar42 >> 0x10) +
                                          (short)((ulonglong)DAT_005f49f0 >> 0x10) + sVar25) >> 4,
                        uVar26);
      uVar29 = CONCAT24((ushort)(sVar34 + (short)((uint6)uVar43 >> 0x20) +
                                          (short)((ulonglong)DAT_005f49f0 >> 0x20) + sVar44) >> 4,
                        uVar28);
      *puVar22 = CONCAT26(((ushort)(sVar47 + (short)uVar12 +
                                   (short)(CONCAT17(uVar8,CONCAT16(cVar59,uVar50)) >> 0x30) + sVar45
                                   ) >> 4) +
                          (short)(CONCAT26((ushort)(sVar38 + (short)(CONCAT17(uVar7,CONCAT16((char)(
                                                  uVar67 >> 0x38),uVar43)) >> 0x30) +
                                                  (short)((ulonglong)DAT_005f49f0 >> 0x30) + sVar45)
                                           >> 4,uVar29) >> 0x28),
                          CONCAT24(((ushort)(sVar37 + (short)uVar11 +
                                            (short)((uint6)uVar50 >> 0x20) + sVar44) >> 4) +
                                   (short)((uint6)uVar29 >> 0x18),
                                   CONCAT22(((ushort)(sVar24 + (short)uVar10 +
                                                     (short)((uint)uVar62 >> 0x10) + sVar25) >> 4) +
                                            (short)((uint)uVar28 >> 8),
                                            ((ushort)(sVar40 + sVar4 + sVar46 + (short)uVar51) >> 4)
                                            + uVar26 * 0x100)));
      uVar66 = *puVar21;
      uVar8 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x18);
      uVar33 = (undefined1)(uVar66 >> 0x18);
      uVar7 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x10);
      uVar31 = (undefined1)(uVar66 >> 0x10);
      uVar6 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 8);
      uVar30 = (undefined1)(uVar66 >> 8);
      uVar5 = (undefined1)(undefined4)DAT_005f4a20;
      sVar41 = CONCAT11(uVar5,(char)uVar66);
      sVar32 = (short)CONCAT31(CONCAT21(CONCAT11(uVar8,uVar33),uVar7),uVar31);
      uVar51 = *puVar17;
      sVar4 = CONCAT11(uVar8,(char)(uVar66 >> 0x20));
      uVar1 = puVar17[1];
      uVar26 = (ushort)((short)uVar1 + CONCAT11(uVar5,uVar30) + (short)DAT_005f49f0 +
                       CONCAT11(uVar5,(char)uVar66) * (short)DAT_005f49d0) >> 4;
      uVar28 = CONCAT22((ushort)((short)((ulonglong)uVar1 >> 0x10) + CONCAT11(uVar6,uVar31) +
                                 (short)((ulonglong)DAT_005f49f0 >> 0x10) +
                                CONCAT11(uVar6,uVar30) * (short)((ulonglong)DAT_005f49d0 >> 0x10))
                        >> 4,uVar26);
      uVar29 = CONCAT24((ushort)((short)((ulonglong)uVar1 >> 0x20) +
                                 (short)CONCAT31(CONCAT21(sVar4,uVar7),uVar33) +
                                 (short)((ulonglong)DAT_005f49f0 >> 0x20) +
                                (short)CONCAT31(CONCAT21(CONCAT11(uVar8,uVar33),uVar7),uVar31) *
                                (short)((ulonglong)DAT_005f49d0 >> 0x20)) >> 4,uVar28);
      *puVar23 = CONCAT26(((ushort)((short)((ulonglong)uVar51 >> 0x30) +
                                    sVar32 + CONCAT11(uVar8,uVar33) *
                                             (short)((ulonglong)DAT_005f49e8 >> 0x30) +
                                   (short)((ulonglong)DAT_005f49f8 >> 0x30)) >> 4) +
                          (short)(CONCAT26((ushort)((short)((ulonglong)uVar1 >> 0x30) + sVar4 +
                                                    (short)((ulonglong)DAT_005f49f0 >> 0x30) +
                                                   CONCAT11(uVar8,uVar33) *
                                                   (short)((ulonglong)DAT_005f49d0 >> 0x30)) >> 4,
                                           uVar29) >> 0x28),
                          CONCAT24(((ushort)((short)((ulonglong)uVar51 >> 0x20) +
                                             CONCAT11(uVar6,uVar30) +
                                             sVar32 * (short)((ulonglong)DAT_005f49e8 >> 0x20) +
                                            (short)((ulonglong)DAT_005f49f8 >> 0x20)) >> 4) +
                                   (short)((uint6)uVar29 >> 0x18),
                                   CONCAT22(((ushort)((short)((ulonglong)uVar51 >> 0x10) +
                                                      sVar41 + CONCAT11(uVar6,uVar30) *
                                                               (short)((ulonglong)DAT_005f49e8 >>
                                                                      0x10) +
                                                     (short)((ulonglong)DAT_005f49f8 >> 0x10)) >> 4)
                                            + (short)((uint)uVar28 >> 8),
                                            ((ushort)((short)uVar51 + sVar41 * (short)DAT_005f49e8 +
                                                     (short)DAT_005f49f8) >> 4) + uVar26 * 0x100)));
      puVar23 = puVar23 + 1;
      puVar17 = puVar17 + 2;
      iVar9 = iVar3;
      while( true ) {
        iVar9 = iVar9 + -8;
        uVar5 = (undefined1)DAT_005f4a20._4_4_;
        uVar6 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 8);
        uVar7 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x10);
        uVar8 = (undefined1)((uint)DAT_005f4a20._4_4_ >> 0x18);
        uVar31 = (undefined1)(uVar66 >> 0x18);
        uVar30 = (undefined1)(uVar66 >> 0x20);
        cVar35 = (char)(uVar66 >> 0x28);
        cVar36 = (char)(uVar66 >> 0x30);
        bVar39 = (byte)(uVar66 >> 0x38);
        sVar47 = (short)DAT_005f49d0;
        sVar27 = (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar40 = (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar24 = (short)((ulonglong)DAT_005f49d0 >> 0x30);
        sVar4 = (short)((ulonglong)DAT_005f49f8 >> 0x10);
        sVar32 = (short)((ulonglong)DAT_005f49f8 >> 0x20);
        sVar38 = (short)((ulonglong)DAT_005f49f8 >> 0x30);
        sVar41 = (short)((ulonglong)DAT_005f49f0 >> 0x10);
        sVar34 = (short)((ulonglong)DAT_005f49f0 >> 0x20);
        sVar37 = (short)((ulonglong)DAT_005f49f0 >> 0x30);
        if (iVar9 < 1) break;
        uVar42 = CONCAT13(uVar6,CONCAT12(cVar35,CONCAT11(uVar5,uVar30)));
        uVar43 = CONCAT15(uVar7,CONCAT14(cVar36,uVar42));
        sVar25 = CONCAT11(uVar5,uVar31);
        uVar62 = CONCAT13(uVar6,CONCAT12(uVar30,sVar25));
        uVar64 = CONCAT15(uVar7,CONCAT14(cVar35,uVar62));
        uVar51 = *puVar17;
        uVar28 = CONCAT13(uVar6,CONCAT12(cVar35,CONCAT11(uVar5,uVar30)));
        uVar50 = CONCAT15(uVar7,CONCAT14(cVar36,uVar28));
        uVar66 = puVar21[1];
        uVar52 = (undefined1)uVar66;
        uVar63 = CONCAT13(uVar6,CONCAT12(cVar36,CONCAT11(uVar5,cVar35)));
        uVar65 = CONCAT15(uVar7,CONCAT14(bVar39,uVar63));
        uVar1 = puVar17[1];
        uVar26 = (ushort)((short)uVar1 + CONCAT11(uVar5,cVar35) + (short)DAT_005f49f0 +
                         CONCAT11(uVar5,uVar30) * sVar47) >> 4;
        uVar28 = CONCAT22((ushort)((short)((ulonglong)uVar1 >> 0x10) +
                                   (short)((uint)uVar63 >> 0x10) + sVar41 +
                                  (short)((uint)uVar28 >> 0x10) * sVar27) >> 4,uVar26);
        uVar29 = CONCAT24((ushort)((short)((ulonglong)uVar1 >> 0x20) +
                                   (short)((uint6)uVar65 >> 0x20) + sVar34 +
                                  (short)((uint6)uVar50 >> 0x20) * sVar40) >> 4,uVar28);
        *puVar23 = CONCAT26(((ushort)((short)((ulonglong)uVar51 >> 0x30) + sVar38 +
                                     (short)(CONCAT17(uVar8,CONCAT16(cVar36,uVar64)) >> 0x30) +
                                     (short)(CONCAT17(uVar8,CONCAT16(bVar39,uVar43)) >> 0x30) *
                                     sVar24) >> 4) +
                            (short)(CONCAT26((ushort)((short)((ulonglong)uVar1 >> 0x30) +
                                                      (short)(CONCAT17(uVar8,CONCAT16(uVar52,uVar65)
                                                                      ) >> 0x30) + sVar37 +
                                                     (short)(CONCAT17(uVar8,CONCAT16(bVar39,uVar50))
                                                            >> 0x30) * sVar24) >> 4,uVar29) >> 0x28)
                            ,CONCAT24(((ushort)((short)((ulonglong)uVar51 >> 0x20) + sVar32 +
                                               (short)((uint6)uVar64 >> 0x20) +
                                               (short)((uint6)uVar43 >> 0x20) * sVar40) >> 4) +
                                      (short)((uint6)uVar29 >> 0x18),
                                      CONCAT22(((ushort)((short)((ulonglong)uVar51 >> 0x10) + sVar4
                                                        + (short)((uint)uVar62 >> 0x10) +
                                                          (short)((uint)uVar42 >> 0x10) * sVar27) >>
                                               4) + (short)((uint)uVar28 >> 8),
                                               ((ushort)((short)uVar51 + (short)DAT_005f49f8 +
                                                        sVar25 + CONCAT11(uVar5,uVar30) * sVar47) >>
                                               4) + uVar26 * 0x100)));
        uVar8 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x18);
        uVar33 = (undefined1)(uVar66 >> 0x18);
        uVar7 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 0x10);
        uVar31 = (undefined1)(uVar66 >> 0x10);
        uVar6 = (undefined1)((uint)(undefined4)DAT_005f4a20 >> 8);
        uVar30 = (undefined1)(uVar66 >> 8);
        uVar5 = (undefined1)(undefined4)DAT_005f4a20;
        sVar37 = (short)CONCAT31(CONCAT21(CONCAT11(uVar8,uVar33),uVar7),uVar31);
        sVar4 = (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar41 = (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar32 = (short)((ulonglong)DAT_005f49d0 >> 0x30);
        uVar51 = puVar17[2];
        sVar34 = CONCAT11(uVar8,(char)(uVar66 >> 0x20));
        uVar1 = puVar17[3];
        uVar26 = (ushort)((short)uVar1 + CONCAT11(uVar5,uVar30) + (short)DAT_005f49f0 +
                         CONCAT11(uVar5,uVar52) * (short)DAT_005f49d0) >> 4;
        uVar28 = CONCAT22((ushort)((short)((ulonglong)uVar1 >> 0x10) + CONCAT11(uVar6,uVar31) +
                                   (short)((ulonglong)DAT_005f49f0 >> 0x10) +
                                  CONCAT11(uVar6,uVar30) * sVar4) >> 4,uVar26);
        uVar29 = CONCAT24((ushort)((short)((ulonglong)uVar1 >> 0x20) +
                                   (short)CONCAT31(CONCAT21(sVar34,uVar7),uVar33) +
                                   (short)((ulonglong)DAT_005f49f0 >> 0x20) +
                                  (short)CONCAT31(CONCAT21(CONCAT11(uVar8,uVar33),uVar7),uVar31) *
                                  sVar41) >> 4,uVar28);
        puVar23[1] = CONCAT26(((ushort)((short)((ulonglong)uVar51 >> 0x30) +
                                        (short)((ulonglong)DAT_005f49f8 >> 0x30) +
                                       sVar37 + CONCAT11(uVar8,uVar33) * sVar32) >> 4) +
                              (short)(CONCAT26((ushort)((short)((ulonglong)uVar1 >> 0x30) + sVar34 +
                                                        (short)((ulonglong)DAT_005f49f0 >> 0x30) +
                                                       CONCAT11(uVar8,uVar33) * sVar32) >> 4,uVar29)
                                     >> 0x28),
                              CONCAT24(((ushort)((short)((ulonglong)uVar51 >> 0x20) +
                                                 (short)((ulonglong)DAT_005f49f8 >> 0x20) +
                                                CONCAT11(uVar6,uVar30) + sVar37 * sVar41) >> 4) +
                                       (short)((uint6)uVar29 >> 0x18),
                                       CONCAT22(((ushort)((short)((ulonglong)uVar51 >> 0x10) +
                                                          (short)((ulonglong)DAT_005f49f8 >> 0x10) +
                                                         CONCAT11(uVar5,uVar52) +
                                                         CONCAT11(uVar6,uVar30) * sVar4) >> 4) +
                                                (short)((uint)uVar28 >> 8),
                                                ((ushort)((short)uVar51 + (short)DAT_005f49f8 +
                                                         (ushort)bVar39 +
                                                         CONCAT11(uVar5,uVar52) *
                                                         (short)DAT_005f49d0) >> 4) + uVar26 * 0x100
                                               )));
        puVar23 = puVar23 + 2;
        puVar21 = puVar21 + 1;
        puVar17 = puVar17 + 4;
      }
      uVar42 = CONCAT13(uVar6,CONCAT12(cVar35,CONCAT11(uVar5,uVar30)));
      uVar43 = CONCAT15(uVar7,CONCAT14(cVar36,uVar42));
      sVar25 = CONCAT11(uVar5,uVar31);
      uVar62 = CONCAT13(uVar6,CONCAT12(uVar30,sVar25));
      uVar64 = CONCAT15(uVar7,CONCAT14(cVar35,uVar62));
      uVar51 = *puVar17;
      uVar28 = CONCAT13(uVar6,CONCAT12(cVar35,CONCAT11(uVar5,uVar30)));
      uVar50 = CONCAT15(uVar7,CONCAT14(cVar36,uVar28));
      uVar66 = uVar66 & _DAT_005f4a10;
      sVar44 = CONCAT11(uVar5,cVar35 + (char)(uVar66 >> 0x20));
      uVar63 = CONCAT13(uVar6,CONCAT12(cVar36 + (char)(uVar66 >> 0x28),sVar44));
      uVar65 = CONCAT15(uVar7,CONCAT14(bVar39 + (char)(uVar66 >> 0x30),uVar63));
      uVar1 = puVar17[1];
      uVar26 = (ushort)((short)uVar1 + sVar44 + (short)DAT_005f49f0 +
                       CONCAT11(uVar5,uVar30) * sVar47) >> 4;
      uVar28 = CONCAT22((ushort)((short)((ulonglong)uVar1 >> 0x10) +
                                 (short)((uint)uVar63 >> 0x10) + sVar41 +
                                (short)((uint)uVar28 >> 0x10) * sVar27) >> 4,uVar26);
      uVar29 = CONCAT24((ushort)((short)((ulonglong)uVar1 >> 0x20) +
                                 (short)((uint6)uVar65 >> 0x20) + sVar34 +
                                (short)((uint6)uVar50 >> 0x20) * sVar40) >> 4,uVar28);
      *puVar23 = CONCAT26(((ushort)((short)((ulonglong)uVar51 >> 0x30) + sVar38 +
                                   (short)(CONCAT17(uVar8,CONCAT16(cVar36,uVar64)) >> 0x30) +
                                   (short)(CONCAT17(uVar8,CONCAT16(bVar39,uVar43)) >> 0x30) * sVar24
                                   ) >> 4) +
                          (short)(CONCAT26((ushort)((short)((ulonglong)uVar1 >> 0x30) +
                                                    (short)(CONCAT17(uVar8,CONCAT16((char)(uVar66 >>
                                                                                          0x38),
                                                                                    uVar65)) >> 0x30
                                                           ) + sVar37 +
                                                   (short)(CONCAT17(uVar8,CONCAT16(bVar39,uVar50))
                                                          >> 0x30) * sVar24) >> 4,uVar29) >> 0x28),
                          CONCAT24(((ushort)((short)((ulonglong)uVar51 >> 0x20) + sVar32 +
                                            (short)((uint6)uVar64 >> 0x20) +
                                            (short)((uint6)uVar43 >> 0x20) * sVar40) >> 4) +
                                   (short)((uint6)uVar29 >> 0x18),
                                   CONCAT22(((ushort)((short)((ulonglong)uVar51 >> 0x10) + sVar4 +
                                                     (short)((uint)uVar62 >> 0x10) +
                                                     (short)((uint)uVar42 >> 0x10) * sVar27) >> 4) +
                                            (short)((uint)uVar28 >> 8),
                                            ((ushort)((short)uVar51 + (short)DAT_005f49f8 +
                                                     sVar25 + CONCAT11(uVar5,uVar30) * sVar47) >> 4)
                                            + uVar26 * 0x100)));
      param_4 = (undefined4 *)((int)param_4 + 4);
    } while (iVar19 < *(int *)(param_3 + 0x13c));
  }
  return;
}
