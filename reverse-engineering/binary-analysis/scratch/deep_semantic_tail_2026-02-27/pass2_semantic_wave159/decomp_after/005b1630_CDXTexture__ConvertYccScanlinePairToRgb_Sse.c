/* address: 0x005b1630 */
/* name: CDXTexture__ConvertYccScanlinePairToRgb_Sse */
/* signature: void __fastcall CDXTexture__ConvertYccScanlinePairToRgb_Sse(int param_1, int param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXTexture__ConvertYccScanlinePairToRgb_Sse(int param_1,int param_2,void *param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  int iVar12;
  int iVar13;
  short sVar14;
  short sVar15;
  short sVar16;
  short sVar17;
  short sVar18;
  short sVar19;
  short sVar20;
  short sVar21;
  int *in_EAX;
  uint uVar22;
  undefined4 *puVar23;
  int iVar24;
  int iVar25;
  undefined4 *puVar26;
  byte *pbVar27;
  byte *pbVar28;
  int iVar29;
  undefined8 *puVar30;
  uint uVar31;
  byte *pbVar32;
  undefined4 *puVar33;
  byte *pbVar34;
  undefined4 *puVar35;
  undefined8 *puVar36;
  undefined8 *puVar37;
  undefined8 *puVar38;
  byte bVar39;
  undefined1 uVar42;
  undefined8 uVar40;
  ulonglong uVar41;
  undefined1 uVar44;
  undefined8 uVar43;
  ulonglong uVar45;
  byte bVar46;
  byte bVar47;
  byte bVar48;
  undefined8 uVar49;
  ulonglong uVar50;
  undefined8 uVar51;
  byte bVar53;
  byte bVar54;
  undefined8 uVar52;
  int local_1c;

  iVar2 = *(int *)(param_1 + 0x148);
  iVar24 = *(int *)(param_1 + 0x1c8);
  iVar3 = *(int *)(iVar24 + 0x10);
  iVar4 = *(int *)(iVar24 + 0x14);
  iVar5 = *(int *)(iVar24 + 0x18);
  iVar24 = *(int *)(iVar24 + 0x1c);
  iVar25 = *(int *)(param_1 + 0x70) >> 3;
  uVar22 = *(int *)(param_1 + 0x70) + iVar25 * -8;
  piVar1 = (int *)(*(int *)param_3 + param_2 * 8);
  puVar6 = (undefined4 *)*piVar1;
  puVar7 = (undefined4 *)piVar1[1];
  puVar8 = *(undefined4 **)(*(int *)((int)param_3 + 4) + param_2 * 4);
  puVar9 = *(undefined4 **)(*(int *)((int)param_3 + 8) + param_2 * 4);
  puVar38 = (undefined8 *)in_EAX[1];
  puVar36 = (undefined8 *)*in_EAX;
  puVar23 = puVar7;
  puVar26 = puVar8;
  puVar30 = puVar38;
  puVar33 = puVar9;
  puVar35 = puVar6;
  puVar37 = puVar36;
  local_1c = iVar25;
  do {
    uVar42 = (undefined1)((uint)*puVar33 >> 8);
    bVar39 = (byte)*puVar33;
    uVar40 = psubsw((ulonglong)
                    CONCAT52(CONCAT41((int)(((uint7)CONCAT21((short)(((uint7)bVar39 << 0x30) >> 0x28
                                                                    ),bVar39) << 0x20) >> 0x18),
                                      bVar39),(ushort)bVar39),0x80008000800080);
    uVar40 = psllw(uVar40,2);
    uVar44 = (undefined1)((uint)*puVar26 >> 8);
    bVar39 = (byte)*puVar26;
    uVar40 = paddsw(uVar40,_DAT_005f4a48);
    uVar40 = pmulhw(uVar40,_DAT_005f4a28);
    uVar43 = psubsw((ulonglong)
                    CONCAT52((int5)(CONCAT43((int)(((uint7)CONCAT21((short)(((uint7)bVar39 << 0x30)
                                                                           >> 0x28),bVar39) << 0x20)
                                                  >> 0x18),CONCAT12(bVar39,CONCAT11(bVar39,bVar39)))
                                   >> 0x10),CONCAT11(bVar39,bVar39)) & 0xffff00ff00ff00ff,
                    0x80008000800080);
    uVar43 = psllw(uVar43,2);
    uVar43 = paddsw(uVar43,_DAT_005f4a50);
    uVar49 = psubsw((ulonglong)
                    CONCAT16(uVar42,(uint6)CONCAT14(uVar42,(uint)(CONCAT12(uVar42,CONCAT11(uVar42,
                                                  uVar42)) & 0xff00ff))),0x80008000800080);
    uVar51 = psubsw((ulonglong)
                    CONCAT16(uVar44,(uint6)CONCAT14(uVar44,(uint)(CONCAT12(uVar44,CONCAT11(uVar44,
                                                  uVar44)) & 0xff00ff))),0x80008000800080);
    uVar43 = pmulhw(uVar43,_DAT_005f4a30);
    uVar49 = psllw(uVar49,2);
    uVar51 = psllw(uVar51,2);
    uVar49 = paddsw(uVar49,_DAT_005f4a58);
    uVar10 = *puVar35;
    uVar49 = pmulhw(uVar49,_DAT_005f4a38);
    bVar54 = (byte)((uint)uVar10 >> 0x18);
    bVar53 = (byte)((uint)uVar10 >> 0x10);
    bVar46 = (byte)((uint)uVar10 >> 8);
    bVar39 = (byte)uVar10;
    uVar51 = paddsw(uVar51,_DAT_005f4a60);
    uVar41 = paddsw(uVar40,uVar43);
    uVar40 = pmulhw(uVar51,_DAT_005f4a40);
    uVar50 = paddsw(uVar49,uVar40);
    uVar43 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar46 << 8,bVar39) << 8,bVar39),
                             (ushort)bVar39),uVar41);
    uVar45 = (uVar41 & 0xffffffff0000) >> 0x10 | (uVar50 & 0xffffffff0000) << 0x10;
    uVar10 = *puVar23;
    uVar40 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar53 << 8,bVar53) << 8,bVar46),
                             (ushort)bVar46),uVar45);
    sVar14 = (short)uVar43;
    sVar15 = (short)((ulonglong)uVar43 >> 0x10);
    sVar16 = (short)((ulonglong)uVar43 >> 0x20);
    sVar17 = (short)((ulonglong)uVar43 >> 0x30);
    sVar18 = (short)uVar40;
    sVar19 = (short)((ulonglong)uVar40 >> 0x10);
    sVar20 = (short)((ulonglong)uVar40 >> 0x20);
    sVar21 = (short)((ulonglong)uVar40 >> 0x30);
    bVar48 = (byte)((uint)uVar10 >> 0x18);
    bVar47 = (byte)((uint)uVar10 >> 0x10);
    bVar46 = (byte)((uint)uVar10 >> 8);
    bVar39 = (byte)uVar10;
    *puVar37 = CONCAT17((0 < sVar21) * (sVar21 < 0x100) * (char)((ulonglong)uVar40 >> 0x30) -
                        (0xff < sVar21),
                        CONCAT16((0 < sVar20) * (sVar20 < 0x100) * (char)((ulonglong)uVar40 >> 0x20)
                                 - (0xff < sVar20),
                                 CONCAT15((0 < sVar19) * (sVar19 < 0x100) *
                                          (char)((ulonglong)uVar40 >> 0x10) - (0xff < sVar19),
                                          CONCAT14((0 < sVar18) * (sVar18 < 0x100) * (char)uVar40 -
                                                   (0xff < sVar18),
                                                   CONCAT13((0 < sVar17) * (sVar17 < 0x100) *
                                                            (char)((ulonglong)uVar43 >> 0x30) -
                                                            (0xff < sVar17),
                                                            CONCAT12((0 < sVar16) * (sVar16 < 0x100)
                                                                     * (char)((ulonglong)uVar43 >>
                                                                             0x20) - (0xff < sVar16)
                                                                     ,CONCAT11((0 < sVar15) *
                                                                               (sVar15 < 0x100) *
                                                                               (char)((ulonglong)
                                                                                      uVar43 >> 0x10
                                                                                     ) - (0xff <
                                                  sVar15),(0 < sVar14) * (sVar14 < 0x100) *
                                                          (char)uVar43 - (0xff < sVar14))))))));
    uVar40 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar46 << 8,bVar39) << 8,bVar39),
                             (ushort)bVar39),uVar41);
    uVar43 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar47 << 8,bVar47) << 8,bVar46),
                             (ushort)bVar46),uVar45);
    sVar14 = (short)uVar40;
    sVar15 = (short)((ulonglong)uVar40 >> 0x10);
    sVar16 = (short)((ulonglong)uVar40 >> 0x20);
    sVar17 = (short)((ulonglong)uVar40 >> 0x30);
    sVar18 = (short)uVar43;
    sVar19 = (short)((ulonglong)uVar43 >> 0x10);
    sVar20 = (short)((ulonglong)uVar43 >> 0x20);
    sVar21 = (short)((ulonglong)uVar43 >> 0x30);
    *puVar30 = CONCAT17((0 < sVar21) * (sVar21 < 0x100) * (char)((ulonglong)uVar43 >> 0x30) -
                        (0xff < sVar21),
                        CONCAT16((0 < sVar20) * (sVar20 < 0x100) * (char)((ulonglong)uVar43 >> 0x20)
                                 - (0xff < sVar20),
                                 CONCAT15((0 < sVar19) * (sVar19 < 0x100) *
                                          (char)((ulonglong)uVar43 >> 0x10) - (0xff < sVar19),
                                          CONCAT14((0 < sVar18) * (sVar18 < 0x100) * (char)uVar43 -
                                                   (0xff < sVar18),
                                                   CONCAT13((0 < sVar17) * (sVar17 < 0x100) *
                                                            (char)((ulonglong)uVar40 >> 0x30) -
                                                            (0xff < sVar17),
                                                            CONCAT12((0 < sVar16) * (sVar16 < 0x100)
                                                                     * (char)((ulonglong)uVar40 >>
                                                                             0x20) - (0xff < sVar16)
                                                                     ,CONCAT11((0 < sVar15) *
                                                                               (sVar15 < 0x100) *
                                                                               (char)((ulonglong)
                                                                                      uVar40 >> 0x10
                                                                                     ) - (0xff <
                                                  sVar15),(0 < sVar14) * (sVar14 < 0x100) *
                                                          (char)uVar40 - (0xff < sVar14))))))));
    uVar43 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar54 << 8,bVar54) << 8,bVar54),
                             (ushort)bVar53),uVar50);
    uVar42 = (undefined1)((uint)*puVar33 >> 0x18);
    bVar39 = (byte)((uint)*puVar33 >> 0x10);
    uVar51 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar48 << 8,bVar48) << 8,bVar48),
                             (ushort)bVar47),uVar50);
    uVar40 = psubsw((ulonglong)
                    CONCAT52(CONCAT41((int)(((uint7)CONCAT21((short)(((uint7)bVar39 << 0x30) >> 0x28
                                                                    ),bVar39) << 0x20) >> 0x18),
                                      bVar39),(ushort)bVar39),0x80008000800080);
    uVar44 = (undefined1)((uint)*puVar26 >> 0x18);
    bVar39 = (byte)((uint)*puVar26 >> 0x10);
    uVar40 = psllw(uVar40,2);
    uVar40 = paddsw(uVar40,_DAT_005f4a48);
    uVar40 = pmulhw(uVar40,_DAT_005f4a28);
    uVar49 = psubsw((ulonglong)
                    CONCAT52((int5)(CONCAT43((int)(((uint7)CONCAT21((short)(((uint7)bVar39 << 0x30)
                                                                           >> 0x28),bVar39) << 0x20)
                                                  >> 0x18),CONCAT12(bVar39,CONCAT11(bVar39,bVar39)))
                                   >> 0x10),CONCAT11(bVar39,bVar39)) & 0xffff00ff00ff00ff,
                    0x80008000800080);
    uVar49 = psllw(uVar49,2);
    uVar49 = paddsw(uVar49,_DAT_005f4a50);
    uVar49 = pmulhw(uVar49,_DAT_005f4a30);
    uVar52 = psubsw((ulonglong)
                    CONCAT16(uVar44,(uint6)CONCAT14(uVar44,(uint)(CONCAT12(uVar44,CONCAT11(uVar44,
                                                  uVar44)) & 0xff00ff))),0x80008000800080);
    uVar41 = paddsw(uVar40,uVar49);
    uVar49 = psllw(uVar52,2);
    uVar40 = psubsw((ulonglong)
                    CONCAT16(uVar42,(uint6)CONCAT14(uVar42,(uint)(CONCAT12(uVar42,CONCAT11(uVar42,
                                                  uVar42)) & 0xff00ff))),0x80008000800080);
    uVar10 = puVar35[1];
    uVar40 = psllw(uVar40,2);
    uVar49 = paddsw(uVar49,_DAT_005f4a60);
    bVar39 = (byte)uVar10;
    uVar40 = paddsw(uVar40,_DAT_005f4a58);
    uVar40 = pmulhw(uVar40,_DAT_005f4a38);
    uVar49 = pmulhw(uVar49,_DAT_005f4a40);
    bVar46 = (byte)((uint)uVar10 >> 8);
    uVar50 = paddsw(uVar40,uVar49);
    uVar40 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar46 << 8,bVar39) << 8,bVar39),
                             (ushort)bVar39),uVar41);
    sVar14 = (short)uVar43;
    sVar15 = (short)((ulonglong)uVar43 >> 0x10);
    sVar16 = (short)((ulonglong)uVar43 >> 0x20);
    sVar17 = (short)((ulonglong)uVar43 >> 0x30);
    sVar18 = (short)uVar40;
    sVar19 = (short)((ulonglong)uVar40 >> 0x10);
    sVar20 = (short)((ulonglong)uVar40 >> 0x20);
    sVar21 = (short)((ulonglong)uVar40 >> 0x30);
    uVar11 = puVar23[1];
    puVar37[1] = CONCAT17((0 < sVar21) * (sVar21 < 0x100) * (char)((ulonglong)uVar40 >> 0x30) -
                          (0xff < sVar21),
                          CONCAT16((0 < sVar20) * (sVar20 < 0x100) *
                                   (char)((ulonglong)uVar40 >> 0x20) - (0xff < sVar20),
                                   CONCAT15((0 < sVar19) * (sVar19 < 0x100) *
                                            (char)((ulonglong)uVar40 >> 0x10) - (0xff < sVar19),
                                            CONCAT14((0 < sVar18) * (sVar18 < 0x100) * (char)uVar40
                                                     - (0xff < sVar18),
                                                     CONCAT13((0 < sVar17) * (sVar17 < 0x100) *
                                                              (char)((ulonglong)uVar43 >> 0x30) -
                                                              (0xff < sVar17),
                                                              CONCAT12((0 < sVar16) *
                                                                       (sVar16 < 0x100) *
                                                                       (char)((ulonglong)uVar43 >>
                                                                             0x20) - (0xff < sVar16)
                                                                       ,CONCAT11((0 < sVar15) *
                                                                                 (sVar15 < 0x100) *
                                                                                 (char)((ulonglong)
                                                                                        uVar43 >>
                                                                                       0x10) -
                                                                                 (0xff < sVar15),
                                                                                 (0 < sVar14) *
                                                                                 (sVar14 < 0x100) *
                                                                                 (char)uVar43 -
                                                                                 (0xff < sVar14)))))
                                           )));
    uVar45 = (uVar41 & 0xffffffff0000) >> 0x10 | (uVar50 & 0xffffffff0000) << 0x10;
    uVar42 = (undefined1)uVar11;
    bVar39 = (byte)((uint)uVar11 >> 8);
    uVar40 = paddsw((ulonglong)
                    CONCAT52((int5)(CONCAT43((int)(((uint7)CONCAT21((short)(((uint7)bVar39 << 0x30)
                                                                           >> 0x28),uVar42) << 0x20)
                                                  >> 0x18),CONCAT12(uVar42,CONCAT11(uVar42,uVar42)))
                                   >> 0x10),CONCAT11(uVar42,uVar42)) & 0xffffffff00ff00ff,uVar41);
    sVar14 = (short)uVar51;
    sVar15 = (short)((ulonglong)uVar51 >> 0x10);
    sVar16 = (short)((ulonglong)uVar51 >> 0x20);
    sVar17 = (short)((ulonglong)uVar51 >> 0x30);
    sVar18 = (short)uVar40;
    sVar19 = (short)((ulonglong)uVar40 >> 0x10);
    sVar20 = (short)((ulonglong)uVar40 >> 0x20);
    sVar21 = (short)((ulonglong)uVar40 >> 0x30);
    bVar48 = (byte)((uint)uVar11 >> 0x10);
    puVar30[1] = CONCAT17((0 < sVar21) * (sVar21 < 0x100) * (char)((ulonglong)uVar40 >> 0x30) -
                          (0xff < sVar21),
                          CONCAT16((0 < sVar20) * (sVar20 < 0x100) *
                                   (char)((ulonglong)uVar40 >> 0x20) - (0xff < sVar20),
                                   CONCAT15((0 < sVar19) * (sVar19 < 0x100) *
                                            (char)((ulonglong)uVar40 >> 0x10) - (0xff < sVar19),
                                            CONCAT14((0 < sVar18) * (sVar18 < 0x100) * (char)uVar40
                                                     - (0xff < sVar18),
                                                     CONCAT13((0 < sVar17) * (sVar17 < 0x100) *
                                                              (char)((ulonglong)uVar51 >> 0x30) -
                                                              (0xff < sVar17),
                                                              CONCAT12((0 < sVar16) *
                                                                       (sVar16 < 0x100) *
                                                                       (char)((ulonglong)uVar51 >>
                                                                             0x20) - (0xff < sVar16)
                                                                       ,CONCAT11((0 < sVar15) *
                                                                                 (sVar15 < 0x100) *
                                                                                 (char)((ulonglong)
                                                                                        uVar51 >>
                                                                                       0x10) -
                                                                                 (0xff < sVar15),
                                                                                 (0 < sVar14) *
                                                                                 (sVar14 < 0x100) *
                                                                                 (char)uVar51 -
                                                                                 (0xff < sVar14)))))
                                           )));
    bVar47 = (byte)((uint)uVar10 >> 0x10);
    uVar51 = paddsw((ulonglong)
                    CONCAT52((int5)(CONCAT43((int)(((uint7)CONCAT21((short)(((uint7)bVar48 << 0x30)
                                                                           >> 0x28),bVar48) << 0x20)
                                                  >> 0x18),CONCAT12(bVar39,CONCAT11(bVar39,bVar39)))
                                   >> 0x10),CONCAT11(bVar39,bVar39)) & 0xffffffff00ff00ff,uVar45);
    uVar49 = paddsw((ulonglong)
                    CONCAT52((int5)(CONCAT43((int)(((uint7)CONCAT21((short)(((uint7)bVar47 << 0x30)
                                                                           >> 0x28),bVar47) << 0x20)
                                                  >> 0x18),CONCAT12(bVar46,CONCAT11(bVar46,bVar46)))
                                   >> 0x10),CONCAT11(bVar46,bVar46)) & 0xffffffff00ff00ff,uVar45);
    bVar46 = (byte)((uint)uVar10 >> 0x18);
    puVar35 = puVar35 + 2;
    puVar23 = puVar23 + 2;
    bVar39 = (byte)((uint)uVar11 >> 0x18);
    uVar40 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar46 << 8,bVar46) << 8,bVar46),
                             (ushort)bVar47),uVar50);
    sVar14 = (short)uVar49;
    sVar15 = (short)((ulonglong)uVar49 >> 0x10);
    sVar16 = (short)((ulonglong)uVar49 >> 0x20);
    sVar17 = (short)((ulonglong)uVar49 >> 0x30);
    sVar18 = (short)uVar40;
    sVar19 = (short)((ulonglong)uVar40 >> 0x10);
    sVar20 = (short)((ulonglong)uVar40 >> 0x20);
    sVar21 = (short)((ulonglong)uVar40 >> 0x30);
    puVar33 = puVar33 + 1;
    uVar43 = paddsw(CONCAT62(CONCAT51((uint5)CONCAT31((uint3)bVar39 << 8,bVar39) << 8,bVar39),
                             (ushort)bVar48),uVar50);
    puVar37[2] = CONCAT17((0 < sVar21) * (sVar21 < 0x100) * (char)((ulonglong)uVar40 >> 0x30) -
                          (0xff < sVar21),
                          CONCAT16((0 < sVar20) * (sVar20 < 0x100) *
                                   (char)((ulonglong)uVar40 >> 0x20) - (0xff < sVar20),
                                   CONCAT15((0 < sVar19) * (sVar19 < 0x100) *
                                            (char)((ulonglong)uVar40 >> 0x10) - (0xff < sVar19),
                                            CONCAT14((0 < sVar18) * (sVar18 < 0x100) * (char)uVar40
                                                     - (0xff < sVar18),
                                                     CONCAT13((0 < sVar17) * (sVar17 < 0x100) *
                                                              (char)((ulonglong)uVar49 >> 0x30) -
                                                              (0xff < sVar17),
                                                              CONCAT12((0 < sVar16) *
                                                                       (sVar16 < 0x100) *
                                                                       (char)((ulonglong)uVar49 >>
                                                                             0x20) - (0xff < sVar16)
                                                                       ,CONCAT11((0 < sVar15) *
                                                                                 (sVar15 < 0x100) *
                                                                                 (char)((ulonglong)
                                                                                        uVar49 >>
                                                                                       0x10) -
                                                                                 (0xff < sVar15),
                                                                                 (0 < sVar14) *
                                                                                 (sVar14 < 0x100) *
                                                                                 (char)uVar49 -
                                                                                 (0xff < sVar14)))))
                                           )));
    sVar14 = (short)uVar51;
    sVar15 = (short)((ulonglong)uVar51 >> 0x10);
    sVar16 = (short)((ulonglong)uVar51 >> 0x20);
    sVar17 = (short)((ulonglong)uVar51 >> 0x30);
    sVar18 = (short)uVar43;
    sVar19 = (short)((ulonglong)uVar43 >> 0x10);
    sVar20 = (short)((ulonglong)uVar43 >> 0x20);
    sVar21 = (short)((ulonglong)uVar43 >> 0x30);
    puVar26 = puVar26 + 1;
    puVar30[2] = CONCAT17((0 < sVar21) * (sVar21 < 0x100) * (char)((ulonglong)uVar43 >> 0x30) -
                          (0xff < sVar21),
                          CONCAT16((0 < sVar20) * (sVar20 < 0x100) *
                                   (char)((ulonglong)uVar43 >> 0x20) - (0xff < sVar20),
                                   CONCAT15((0 < sVar19) * (sVar19 < 0x100) *
                                            (char)((ulonglong)uVar43 >> 0x10) - (0xff < sVar19),
                                            CONCAT14((0 < sVar18) * (sVar18 < 0x100) * (char)uVar43
                                                     - (0xff < sVar18),
                                                     CONCAT13((0 < sVar17) * (sVar17 < 0x100) *
                                                              (char)((ulonglong)uVar51 >> 0x30) -
                                                              (0xff < sVar17),
                                                              CONCAT12((0 < sVar16) *
                                                                       (sVar16 < 0x100) *
                                                                       (char)((ulonglong)uVar51 >>
                                                                             0x20) - (0xff < sVar16)
                                                                       ,CONCAT11((0 < sVar15) *
                                                                                 (sVar15 < 0x100) *
                                                                                 (char)((ulonglong)
                                                                                        uVar51 >>
                                                                                       0x10) -
                                                                                 (0xff < sVar15),
                                                                                 (0 < sVar14) *
                                                                                 (sVar14 < 0x100) *
                                                                                 (char)uVar51 -
                                                                                 (0xff < sVar14)))))
                                           )));
    local_1c = local_1c + -1;
    puVar30 = puVar30 + 3;
    puVar37 = puVar37 + 3;
  } while (local_1c != 0);
  pbVar27 = (byte *)(puVar8 + iVar25);
  pbVar28 = (byte *)(puVar9 + iVar25);
  pbVar32 = (byte *)(puVar6 + iVar25 * 2);
  pbVar34 = (byte *)(puVar7 + iVar25 * 2);
  puVar36 = puVar36 + iVar25 * 3;
  puVar38 = puVar38 + iVar25 * 3;
  for (iVar25 = (int)uVar22 >> 1; iVar25 != 0; iVar25 = iVar25 + -1) {
    bVar39 = *pbVar27;
    pbVar27 = pbVar27 + 1;
    bVar46 = *pbVar28;
    pbVar28 = pbVar28 + 1;
    iVar12 = *(int *)(iVar3 + (uint)bVar46 * 4);
    iVar13 = *(int *)(iVar4 + (uint)bVar39 * 4);
    uVar31 = (uint)*pbVar32;
    iVar29 = *(int *)(iVar24 + (uint)bVar39 * 4) + *(int *)(iVar5 + (uint)bVar46 * 4) >> 0x10;
    *(undefined1 *)puVar36 = *(undefined1 *)(uVar31 + iVar12 + iVar2);
    *(undefined1 *)((int)puVar36 + 1) = *(undefined1 *)(uVar31 + iVar29 + iVar2);
    *(undefined1 *)((int)puVar36 + 2) = *(undefined1 *)(uVar31 + iVar13 + iVar2);
    uVar31 = (uint)pbVar32[1];
    pbVar32 = pbVar32 + 2;
    *(undefined1 *)((int)puVar36 + 3) = *(undefined1 *)(uVar31 + iVar12 + iVar2);
    *(undefined1 *)((int)puVar36 + 4) = *(undefined1 *)(uVar31 + iVar29 + iVar2);
    *(undefined1 *)((int)puVar36 + 5) = *(undefined1 *)(uVar31 + iVar13 + iVar2);
    uVar31 = (uint)*pbVar34;
    puVar36 = (undefined8 *)((int)puVar36 + 6);
    *(undefined1 *)puVar38 = *(undefined1 *)(uVar31 + iVar12 + iVar2);
    *(undefined1 *)((int)puVar38 + 1) = *(undefined1 *)(uVar31 + iVar29 + iVar2);
    *(undefined1 *)((int)puVar38 + 2) = *(undefined1 *)(uVar31 + iVar13 + iVar2);
    uVar31 = (uint)pbVar34[1];
    pbVar34 = pbVar34 + 2;
    *(undefined1 *)((int)puVar38 + 3) = *(undefined1 *)(iVar12 + uVar31 + iVar2);
    *(undefined1 *)((int)puVar38 + 4) = *(undefined1 *)(iVar29 + uVar31 + iVar2);
    *(undefined1 *)((int)puVar38 + 5) = *(undefined1 *)(uVar31 + iVar13 + iVar2);
    puVar38 = (undefined8 *)((int)puVar38 + 6);
  }
  if ((uVar22 & 1) != 0) {
    iVar3 = *(int *)(iVar3 + (uint)*pbVar28 * 4);
    iVar24 = *(int *)(iVar24 + (uint)*pbVar27 * 4);
    iVar5 = *(int *)(iVar5 + (uint)*pbVar28 * 4);
    iVar4 = *(int *)(iVar4 + (uint)*pbVar27 * 4);
    uVar22 = (uint)*pbVar32;
    *(undefined1 *)puVar36 = *(undefined1 *)(uVar22 + iVar3 + iVar2);
    iVar24 = iVar24 + iVar5 >> 0x10;
    *(undefined1 *)((int)puVar36 + 1) = *(undefined1 *)(uVar22 + iVar24 + iVar2);
    *(undefined1 *)((int)puVar36 + 2) = *(undefined1 *)(uVar22 + iVar4 + iVar2);
    uVar22 = (uint)*pbVar34;
    *(undefined1 *)puVar38 = *(undefined1 *)(iVar3 + uVar22 + iVar2);
    uVar42 = *(undefined1 *)(uVar22 + iVar4 + iVar2);
    *(undefined1 *)((int)puVar38 + 1) = *(undefined1 *)(iVar24 + uVar22 + iVar2);
    *(undefined1 *)((int)puVar38 + 2) = uVar42;
  }
  return;
}
