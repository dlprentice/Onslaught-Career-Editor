/* address: 0x0058d8c2 */
/* name: CTexture__Helper_0058d8c2 */
/* signature: uint __thiscall CTexture__Helper_0058d8c2(void * this, int param_1, void * param_2) */


uint __thiscall CTexture__Helper_0058d8c2(void *this,int param_1,void *param_2)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  byte bVar6;
  byte bVar7;
  uint uVar8;
  byte *pbVar9;
  int iVar10;
  uint extraout_EAX;
  uint extraout_EAX_00;
  uint uVar11;
  uint uVar12;
  byte *pbVar13;
  byte *pbVar14;
  int unaff_EDI;
  int iVar15;
  byte *pbVar16;
  bool bVar17;
  bool bVar18;
  bool bVar19;
  bool bVar20;
  bool bVar21;
  uint local_50;
  uint local_4c;
  uint local_48;
  int local_44;
  byte *local_20;
  byte local_10 [16];

  local_20 = *(byte **)(param_1 + 8);
  *(undefined4 *)((int)this + 0x54) = 0;
  local_50 = 0x10d;
  local_44 = 0;
  local_4c = 0;
  local_48 = 0;
  bVar17 = true;
  bVar19 = false;
  bVar1 = false;
  bVar2 = false;
  bVar20 = false;
  bVar4 = false;
  bVar5 = false;
  bVar21 = false;
  bVar3 = false;
  if (*local_20 == 0) {
LAB_0058e22f:
    *(undefined4 *)((int)this + 0x54) = 0;
    *(int *)((int)this + 0x40) = local_44;
    *(uint *)((int)this + 0x44) = local_4c;
    *(uint *)((int)this + 0x48) = local_48;
  }
  else {
    do {
      for (param_1 = (int)local_20; (*(char *)param_1 != '\0' && (*(char *)param_1 != '_'));
          param_1 = param_1 + 1) {
      }
      uVar8 = param_1 - (int)local_20;
      if (0xf < uVar8) goto LAB_0058e228;
      pbVar9 = local_10;
      for (uVar11 = uVar8 >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
        *(undefined4 *)pbVar9 = *(undefined4 *)local_20;
        local_20 = local_20 + 4;
        pbVar9 = pbVar9 + 4;
      }
      pbVar13 = (byte *)0x3;
      for (uVar11 = uVar8 & 3; uVar11 != 0; uVar11 = uVar11 - 1) {
        *pbVar9 = *local_20;
        local_20 = local_20 + 1;
        pbVar9 = pbVar9 + 1;
      }
      local_10[uVar8] = 0;
      if (*(char *)param_1 != '\0') {
        param_1 = param_1 + 1;
      }
      if (bVar17) {
        iVar15 = 0;
        uVar8 = 0;
        do {
          pbVar13 = *(byte **)((int)&PTR_DAT_005ea930 + uVar8);
          pbVar9 = local_10;
          do {
            bVar7 = *pbVar9;
            bVar17 = bVar7 < *pbVar13;
            if (bVar7 != *pbVar13) {
LAB_0058d9b2:
              iVar10 = (1 - (uint)bVar17) - (uint)(bVar17 != 0);
              goto LAB_0058d9b7;
            }
            if (bVar7 == 0) break;
            bVar7 = pbVar9[1];
            bVar17 = bVar7 < pbVar13[1];
            if (bVar7 != pbVar13[1]) goto LAB_0058d9b2;
            pbVar9 = pbVar9 + 2;
            pbVar13 = pbVar13 + 2;
          } while (bVar7 != 0);
          iVar10 = 0;
LAB_0058d9b7:
          if (iVar10 == 0) break;
          uVar8 = uVar8 + 0x44;
          iVar15 = iVar15 + 1;
        } while (uVar8 < 0x1650);
        if (iVar15 == 0x54) goto LAB_0058e228;
        iVar10 = *(int *)((int)this + 0x38);
        uVar8 = *(uint *)(&DAT_005ea938 + (iVar15 * 0x11 + iVar10) * 4);
        if (uVar8 < 0xfffffffb) {
          if (uVar8 == 0xfffffffa) {
            local_50 = 0x10c;
          }
          else if (uVar8 == 0) {
            local_50 = 0x102;
          }
          else if (uVar8 == 1) {
            local_50 = 0x103;
          }
          else if (uVar8 == 2) {
            local_50 = 0x104;
          }
          else if (uVar8 == 3) {
            local_50 = 0x105;
          }
          else if (uVar8 == 4) {
            local_50 = 0x106;
          }
          else if (uVar8 == 5) {
            local_50 = 0x107;
          }
        }
        else if (uVar8 == 0xfffffffb) {
          local_50 = 0x10b;
        }
        else if (uVar8 == 0xfffffffc) {
          local_50 = 0x10a;
        }
        else if (uVar8 == 0xfffffffd) {
          local_50 = 0x108;
        }
        else if (uVar8 == 0xfffffffe) {
          local_50 = 0x109;
        }
        else if (uVar8 == 0xffffffff) {
          *(undefined4 *)((int)this + 0x54) = 0x7e7;
          goto LAB_0058e228;
        }
        bVar17 = false;
        local_44 = (&DAT_005ea934)[iVar15 * 0x11];
        if ((((5 < iVar10) && (iVar10 < 10)) && (0x102 < local_50)) && (local_50 < 0x108)) {
          bVar19 = true;
        }
        if ((((3 < iVar10) && (iVar10 < 6)) || ((5 < iVar10 && (iVar10 < 0xf)))) &&
           ((0x102 < local_50 && (local_50 < 0x108)))) {
          bVar1 = true;
        }
        if (((0xc < iVar10) && (iVar10 < 0xf)) &&
           ((local_44 == 0x5b || (((local_44 == 0x5c || (local_44 == 0x1f)) || (local_44 == 0x42))))
           )) {
          bVar2 = true;
        }
        if (((9 < iVar10) && (iVar10 < 0xf)) && ((0x102 < local_50 && (local_50 < 0x108)))) {
          bVar3 = true;
        }
        if ((((3 < iVar10) && (iVar10 < 6)) || ((9 < iVar10 && (iVar10 < 0xf)))) &&
           (local_44 == 0x1f)) {
          bVar20 = true;
        }
        if (((0xc < iVar10) && (iVar10 < 0xf)) && (local_44 == 0x1f)) {
          bVar4 = true;
        }
        if (((-1 < iVar10) && (iVar10 < 6)) && (local_44 == 0x1f)) {
          bVar5 = true;
        }
        if (((local_44 == 0x28) || (local_44 == 0x2c)) || (local_44 == 0x5e)) {
          bVar21 = true;
        }
        *(undefined4 *)((int)this + 0x54) = 0x7e8;
      }
      else {
        pbVar9 = (byte *)0x0;
        if (bVar1) {
          pbVar9 = (byte *)0x4;
          bVar18 = true;
          pbVar14 = local_10;
          pbVar16 = &DAT_005eca90;
          do {
            if (pbVar9 == (byte *)0x0) break;
            pbVar9 = pbVar9 + -1;
            bVar18 = *pbVar14 == *pbVar16;
            pbVar14 = pbVar14 + 1;
            pbVar16 = pbVar16 + 1;
          } while (bVar18);
          if (bVar18) {
            local_4c = local_4c | 0x100000;
            bVar19 = false;
            bVar1 = false;
            goto LAB_0058e1b0;
          }
        }
        if (bVar2) {
          pbVar9 = (byte *)0x9;
          bVar18 = true;
          pbVar14 = local_10;
          pbVar16 = (byte *)"centroid";
          do {
            if (pbVar9 == (byte *)0x0) break;
            pbVar9 = pbVar9 + -1;
            bVar18 = *pbVar14 == *pbVar16;
            pbVar14 = pbVar14 + 1;
            pbVar16 = pbVar16 + 1;
          } while (bVar18);
          if (bVar18) {
            local_4c = local_4c | 0x400000;
            bVar2 = false;
            goto LAB_0058e1b0;
          }
        }
        if (bVar19) {
          bVar19 = true;
          pbVar9 = pbVar13;
          pbVar14 = local_10;
          pbVar16 = &DAT_005eca80;
          do {
            if (pbVar9 == (byte *)0x0) break;
            pbVar9 = pbVar9 + -1;
            bVar19 = *pbVar14 == *pbVar16;
            pbVar14 = pbVar14 + 1;
            pbVar16 = pbVar16 + 1;
          } while (bVar19);
          if (bVar19) {
            local_4c = 0x3000000;
          }
          else {
            bVar19 = true;
            pbVar9 = pbVar13;
            pbVar14 = local_10;
            pbVar16 = &DAT_005eca7c;
            do {
              if (pbVar9 == (byte *)0x0) break;
              pbVar9 = pbVar9 + -1;
              bVar19 = *pbVar14 == *pbVar16;
              pbVar14 = pbVar14 + 1;
              pbVar16 = pbVar16 + 1;
            } while (bVar19);
            if (bVar19) {
              local_4c = 0x2000000;
            }
            else {
              bVar19 = true;
              pbVar9 = pbVar13;
              pbVar14 = local_10;
              pbVar16 = &DAT_005eca78;
              do {
                if (pbVar9 == (byte *)0x0) break;
                pbVar9 = pbVar9 + -1;
                bVar19 = *pbVar14 == *pbVar16;
                pbVar14 = pbVar14 + 1;
                pbVar16 = pbVar16 + 1;
              } while (bVar19);
              if (bVar19) {
                local_4c = 0x1000000;
              }
              else {
                bVar19 = true;
                pbVar9 = pbVar13;
                pbVar14 = local_10;
                pbVar16 = &DAT_005eca74;
                do {
                  if (pbVar9 == (byte *)0x0) break;
                  pbVar9 = pbVar9 + -1;
                  bVar19 = *pbVar14 == *pbVar16;
                  pbVar14 = pbVar14 + 1;
                  pbVar16 = pbVar16 + 1;
                } while (bVar19);
                if (bVar19) {
                  local_4c = 0xf000000;
                }
                else {
                  bVar19 = true;
                  pbVar9 = pbVar13;
                  pbVar14 = local_10;
                  pbVar16 = &DAT_005eca70;
                  do {
                    if (pbVar9 == (byte *)0x0) break;
                    pbVar9 = pbVar9 + -1;
                    bVar19 = *pbVar14 == *pbVar16;
                    pbVar14 = pbVar14 + 1;
                    pbVar16 = pbVar16 + 1;
                  } while (bVar19);
                  if (bVar19) {
                    local_4c = 0xe000000;
                  }
                  else {
                    bVar19 = true;
                    pbVar9 = local_10;
                    pbVar14 = &DAT_005eca6c;
                    do {
                      if (pbVar13 == (byte *)0x0) break;
                      pbVar13 = pbVar13 + -1;
                      bVar19 = *pbVar9 == *pbVar14;
                      pbVar9 = pbVar9 + 1;
                      pbVar14 = pbVar14 + 1;
                    } while (bVar19);
                    if (!bVar19) goto LAB_0058e228;
                    local_4c = 0xd000000;
                  }
                }
              }
            }
          }
          bVar19 = false;
        }
        else {
          if (bVar20) {
            uVar8 = 0;
            bVar20 = true;
            pbVar9 = pbVar13;
            pbVar14 = local_10;
            pbVar16 = &DAT_005eca68;
            do {
              if (pbVar9 == (byte *)0x0) break;
              pbVar9 = pbVar9 + -1;
              bVar20 = *pbVar14 == *pbVar16;
              pbVar14 = pbVar14 + 1;
              pbVar16 = pbVar16 + 1;
            } while (bVar20);
            if (bVar20) {
              uVar8 = 0x10000000;
            }
            else {
              pbVar9 = (byte *)0x5;
              bVar20 = true;
              pbVar14 = local_10;
              pbVar16 = &DAT_005eca60;
              do {
                if (pbVar9 == (byte *)0x0) break;
                pbVar9 = pbVar9 + -1;
                bVar20 = *pbVar14 == *pbVar16;
                pbVar14 = pbVar14 + 1;
                pbVar16 = pbVar16 + 1;
              } while (bVar20);
              if (bVar20) {
                uVar8 = 0x18000000;
              }
              else {
                pbVar9 = (byte *)0x7;
                bVar20 = true;
                pbVar14 = local_10;
                pbVar16 = (byte *)"volume";
                do {
                  if (pbVar9 == (byte *)0x0) break;
                  pbVar9 = pbVar9 + -1;
                  bVar20 = *pbVar14 == *pbVar16;
                  pbVar14 = pbVar14 + 1;
                  pbVar16 = pbVar16 + 1;
                } while (bVar20);
                if (bVar20) {
                  uVar8 = 0x20000000;
                }
              }
            }
            local_48 = local_48 | uVar8;
            bVar20 = false;
            if (uVar8 != 0) {
              bVar4 = false;
              bVar5 = false;
              goto LAB_0058e1b0;
            }
          }
          if (bVar3) {
            bVar18 = true;
            pbVar9 = local_10;
            pbVar14 = &DAT_005eca54;
            do {
              if (pbVar13 == (byte *)0x0) break;
              pbVar13 = pbVar13 + -1;
              bVar18 = *pbVar9 == *pbVar14;
              pbVar9 = pbVar9 + 1;
              pbVar14 = pbVar14 + 1;
            } while (bVar18);
            pbVar9 = pbVar13;
            if (bVar18) {
              local_4c = local_4c | 0x200000;
              bVar3 = false;
              goto LAB_0058e1b0;
            }
          }
          if (bVar4) {
            pbVar13 = local_10;
            if (local_10[0] == 0) {
LAB_0058dd6c:
              uVar8 = 0;
            }
            else {
              do {
                pbVar14 = (byte *)(int)(char)*pbVar13;
                uVar8 = CRT__IsAlpha_0056a05b(pbVar9,(byte *)(int)(char)*pbVar13,unaff_EDI);
                pbVar9 = pbVar14;
                if (uVar8 == 0) break;
                pbVar13 = pbVar13 + 1;
              } while (*pbVar13 != 0);
              if (*pbVar13 == 0) goto LAB_0058dd6c;
              pbVar9 = pbVar13;
              CSoundManager__Helper_0055e2a6(pbVar13);
              uVar8 = extraout_EAX;
            }
            if (uVar8 < 0x10) {
              bVar7 = *pbVar13;
              pbVar14 = pbVar13;
              if (bVar7 != 0) {
                *pbVar13 = 0;
                pbVar14 = pbVar13 + 1;
              }
              bVar6 = *pbVar14;
              if (bVar6 == 0) {
LAB_0058dda9:
                pbVar9 = (byte *)0x9;
                uVar11 = 0;
                bVar18 = true;
                pbVar14 = local_10;
                pbVar16 = (byte *)"position";
                do {
                  if (pbVar9 == (byte *)0x0) break;
                  pbVar9 = pbVar9 + -1;
                  bVar18 = *pbVar14 == *pbVar16;
                  pbVar14 = pbVar14 + 1;
                  pbVar16 = pbVar16 + 1;
                } while (bVar18);
                if (bVar18) {
                  if (uVar8 == 0) goto LAB_0058df19;
                }
                else {
                  iVar15 = 0xc;
                  bVar18 = true;
                  pbVar9 = local_10;
                  pbVar14 = (byte *)"blendweight";
                  do {
                    if (iVar15 == 0) break;
                    iVar15 = iVar15 + -1;
                    bVar18 = *pbVar9 == *pbVar14;
                    pbVar9 = pbVar9 + 1;
                    pbVar14 = pbVar14 + 1;
                  } while (bVar18);
                  if (bVar18) {
                    uVar11 = 1;
                  }
                  else {
                    iVar15 = 0xd;
                    bVar18 = true;
                    pbVar9 = local_10;
                    pbVar14 = (byte *)"blendindices";
                    do {
                      if (iVar15 == 0) break;
                      iVar15 = iVar15 + -1;
                      bVar18 = *pbVar9 == *pbVar14;
                      pbVar9 = pbVar9 + 1;
                      pbVar14 = pbVar14 + 1;
                    } while (bVar18);
                    if (bVar18) {
                      uVar11 = 2;
                    }
                    else {
                      iVar15 = 7;
                      bVar18 = true;
                      pbVar9 = local_10;
                      pbVar14 = (byte *)"normal";
                      do {
                        if (iVar15 == 0) break;
                        iVar15 = iVar15 + -1;
                        bVar18 = *pbVar9 == *pbVar14;
                        pbVar9 = pbVar9 + 1;
                        pbVar14 = pbVar14 + 1;
                      } while (bVar18);
                      if (bVar18) {
                        uVar11 = 3;
                      }
                      else {
                        uVar11 = 6;
                        bVar18 = true;
                        uVar12 = uVar11;
                        pbVar9 = local_10;
                        pbVar14 = (byte *)"psize";
                        do {
                          if (uVar12 == 0) break;
                          uVar12 = uVar12 - 1;
                          bVar18 = *pbVar9 == *pbVar14;
                          pbVar9 = pbVar9 + 1;
                          pbVar14 = pbVar14 + 1;
                        } while (bVar18);
                        if (bVar18) {
                          uVar11 = 4;
                        }
                        else {
                          iVar15 = 9;
                          bVar18 = true;
                          pbVar9 = local_10;
                          pbVar14 = (byte *)"texcoord";
                          do {
                            if (iVar15 == 0) break;
                            iVar15 = iVar15 + -1;
                            bVar18 = *pbVar9 == *pbVar14;
                            pbVar9 = pbVar9 + 1;
                            pbVar14 = pbVar14 + 1;
                          } while (bVar18);
                          if (bVar18) {
                            uVar11 = 5;
                          }
                          else {
                            iVar15 = 8;
                            bVar18 = true;
                            pbVar9 = local_10;
                            pbVar14 = (byte *)"tangent";
                            do {
                              if (iVar15 == 0) break;
                              iVar15 = iVar15 + -1;
                              bVar18 = *pbVar9 == *pbVar14;
                              pbVar9 = pbVar9 + 1;
                              pbVar14 = pbVar14 + 1;
                            } while (bVar18);
                            if (!bVar18) {
                              iVar15 = 9;
                              bVar18 = true;
                              pbVar9 = local_10;
                              pbVar14 = (byte *)"binormal";
                              do {
                                if (iVar15 == 0) break;
                                iVar15 = iVar15 + -1;
                                bVar18 = *pbVar9 == *pbVar14;
                                pbVar9 = pbVar9 + 1;
                                pbVar14 = pbVar14 + 1;
                              } while (bVar18);
                              if (bVar18) {
                                uVar11 = 7;
                              }
                              else {
                                iVar15 = 0xb;
                                bVar18 = true;
                                pbVar9 = local_10;
                                pbVar14 = (byte *)"tessfactor";
                                do {
                                  if (iVar15 == 0) break;
                                  iVar15 = iVar15 + -1;
                                  bVar18 = *pbVar9 == *pbVar14;
                                  pbVar9 = pbVar9 + 1;
                                  pbVar14 = pbVar14 + 1;
                                } while (bVar18);
                                if (bVar18) {
                                  uVar11 = 8;
                                }
                                else {
                                  uVar11 = 10;
                                  bVar18 = true;
                                  uVar12 = uVar11;
                                  pbVar9 = local_10;
                                  pbVar14 = (byte *)"positiont";
                                  do {
                                    if (uVar12 == 0) break;
                                    uVar12 = uVar12 - 1;
                                    bVar18 = *pbVar9 == *pbVar14;
                                    pbVar9 = pbVar9 + 1;
                                    pbVar14 = pbVar14 + 1;
                                  } while (bVar18);
                                  if (bVar18) {
                                    uVar11 = 9;
                                  }
                                  else {
                                    iVar15 = 6;
                                    bVar18 = true;
                                    pbVar9 = local_10;
                                    pbVar14 = (byte *)"color";
                                    do {
                                      if (iVar15 == 0) break;
                                      iVar15 = iVar15 + -1;
                                      bVar18 = *pbVar9 == *pbVar14;
                                      pbVar9 = pbVar9 + 1;
                                      pbVar14 = pbVar14 + 1;
                                    } while (bVar18);
                                    if (!bVar18) {
                                      iVar15 = 4;
                                      bVar18 = true;
                                      pbVar9 = local_10;
                                      pbVar14 = &DAT_005ec9e4;
                                      do {
                                        if (iVar15 == 0) break;
                                        iVar15 = iVar15 + -1;
                                        bVar18 = *pbVar9 == *pbVar14;
                                        pbVar9 = pbVar9 + 1;
                                        pbVar14 = pbVar14 + 1;
                                      } while (bVar18);
                                      if (bVar18) {
                                        uVar11 = 0xb;
                                      }
                                      else {
                                        iVar15 = 6;
                                        bVar18 = true;
                                        pbVar9 = local_10;
                                        pbVar14 = (byte *)"depth";
                                        do {
                                          if (iVar15 == 0) break;
                                          iVar15 = iVar15 + -1;
                                          bVar18 = *pbVar9 == *pbVar14;
                                          pbVar9 = pbVar9 + 1;
                                          pbVar14 = pbVar14 + 1;
                                        } while (bVar18);
                                        if (bVar18) {
                                          uVar11 = 0xc;
                                        }
                                        else {
                                          pbVar9 = (byte *)0x7;
                                          bVar18 = true;
                                          pbVar14 = local_10;
                                          pbVar16 = (byte *)"sample";
                                          do {
                                            if (pbVar9 == (byte *)0x0) break;
                                            pbVar9 = pbVar9 + -1;
                                            bVar18 = *pbVar14 == *pbVar16;
                                            pbVar14 = pbVar14 + 1;
                                            pbVar16 = pbVar16 + 1;
                                          } while (bVar18);
                                          if (!bVar18) goto LAB_0058df19;
                                          uVar11 = 0xd;
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
                bVar4 = false;
                local_48 = local_48 | (uVar8 & 0xf) << 0x10 | uVar11;
                bVar20 = false;
                goto LAB_0058e1b0;
              }
              do {
                pbVar16 = (byte *)(int)(char)bVar6;
                uVar11 = CRT__IsDigit_0056a089(pbVar9,(byte *)(int)(char)bVar6,unaff_EDI);
                pbVar9 = pbVar16;
                if (uVar11 == 0) break;
                pbVar14 = pbVar14 + 1;
                bVar6 = *pbVar14;
              } while (bVar6 != 0);
              if (*pbVar14 == 0) goto LAB_0058dda9;
LAB_0058df19:
              *pbVar13 = bVar7;
            }
          }
          iVar15 = 3;
          if (bVar5) {
            pbVar13 = local_10;
            if (local_10[0] == 0) {
LAB_0058df61:
              uVar8 = 0;
            }
            else {
              do {
                pbVar14 = (byte *)(int)(char)*pbVar13;
                uVar8 = CRT__IsAlpha_0056a05b(pbVar9,(byte *)(int)(char)*pbVar13,unaff_EDI);
                pbVar9 = pbVar14;
                if (uVar8 == 0) break;
                pbVar13 = pbVar13 + 1;
              } while (*pbVar13 != 0);
              if (*pbVar13 == 0) goto LAB_0058df61;
              pbVar9 = pbVar13;
              CSoundManager__Helper_0055e2a6(pbVar13);
              uVar8 = extraout_EAX_00;
            }
            if (0xf < uVar8) goto LAB_0058e228;
            if (*pbVar13 != 0) {
              *pbVar13 = 0;
              pbVar13 = pbVar13 + 1;
            }
            bVar7 = *pbVar13;
            if (bVar7 != 0) {
              do {
                pbVar14 = (byte *)(int)(char)bVar7;
                uVar11 = CRT__IsDigit_0056a089(pbVar9,(byte *)(int)(char)bVar7,unaff_EDI);
                pbVar9 = pbVar14;
                if (uVar11 == 0) break;
                pbVar13 = pbVar13 + 1;
                bVar7 = *pbVar13;
              } while (bVar7 != 0);
              if (*pbVar13 != 0) goto LAB_0058e228;
            }
            iVar15 = 9;
            local_48 = 0;
            bVar20 = true;
            pbVar9 = local_10;
            pbVar13 = (byte *)"position";
            do {
              if (iVar15 == 0) break;
              iVar15 = iVar15 + -1;
              bVar20 = *pbVar9 == *pbVar13;
              pbVar9 = pbVar9 + 1;
              pbVar13 = pbVar13 + 1;
            } while (bVar20);
            if (!bVar20) {
              iVar15 = 0xc;
              bVar20 = true;
              pbVar9 = local_10;
              pbVar13 = (byte *)"blendweight";
              do {
                if (iVar15 == 0) break;
                iVar15 = iVar15 + -1;
                bVar20 = *pbVar9 == *pbVar13;
                pbVar9 = pbVar9 + 1;
                pbVar13 = pbVar13 + 1;
              } while (bVar20);
              if (bVar20) {
                local_48 = 1;
              }
              else {
                iVar15 = 0xd;
                bVar20 = true;
                pbVar9 = local_10;
                pbVar13 = (byte *)"blendindices";
                do {
                  if (iVar15 == 0) break;
                  iVar15 = iVar15 + -1;
                  bVar20 = *pbVar9 == *pbVar13;
                  pbVar9 = pbVar9 + 1;
                  pbVar13 = pbVar13 + 1;
                } while (bVar20);
                if (bVar20) {
                  local_48 = 2;
                }
                else {
                  iVar15 = 7;
                  bVar20 = true;
                  pbVar9 = local_10;
                  pbVar13 = (byte *)"normal";
                  do {
                    if (iVar15 == 0) break;
                    iVar15 = iVar15 + -1;
                    bVar20 = *pbVar9 == *pbVar13;
                    pbVar9 = pbVar9 + 1;
                    pbVar13 = pbVar13 + 1;
                  } while (bVar20);
                  if (bVar20) {
                    local_48 = 3;
                  }
                  else {
                    local_48 = 6;
                    bVar20 = true;
                    uVar11 = local_48;
                    pbVar9 = local_10;
                    pbVar13 = (byte *)"psize";
                    do {
                      if (uVar11 == 0) break;
                      uVar11 = uVar11 - 1;
                      bVar20 = *pbVar9 == *pbVar13;
                      pbVar9 = pbVar9 + 1;
                      pbVar13 = pbVar13 + 1;
                    } while (bVar20);
                    if (bVar20) {
                      local_48 = 4;
                    }
                    else {
                      iVar15 = 9;
                      bVar20 = true;
                      pbVar9 = local_10;
                      pbVar13 = (byte *)"texcoord";
                      do {
                        if (iVar15 == 0) break;
                        iVar15 = iVar15 + -1;
                        bVar20 = *pbVar9 == *pbVar13;
                        pbVar9 = pbVar9 + 1;
                        pbVar13 = pbVar13 + 1;
                      } while (bVar20);
                      if (bVar20) {
                        local_48 = 5;
                      }
                      else {
                        iVar15 = 8;
                        bVar20 = true;
                        pbVar9 = local_10;
                        pbVar13 = (byte *)"tangent";
                        do {
                          if (iVar15 == 0) break;
                          iVar15 = iVar15 + -1;
                          bVar20 = *pbVar9 == *pbVar13;
                          pbVar9 = pbVar9 + 1;
                          pbVar13 = pbVar13 + 1;
                        } while (bVar20);
                        if (!bVar20) {
                          iVar15 = 9;
                          bVar20 = true;
                          pbVar9 = local_10;
                          pbVar13 = (byte *)"binormal";
                          do {
                            if (iVar15 == 0) break;
                            iVar15 = iVar15 + -1;
                            bVar20 = *pbVar9 == *pbVar13;
                            pbVar9 = pbVar9 + 1;
                            pbVar13 = pbVar13 + 1;
                          } while (bVar20);
                          if (bVar20) {
                            local_48 = 7;
                          }
                          else {
                            iVar15 = 0xb;
                            bVar20 = true;
                            pbVar9 = local_10;
                            pbVar13 = (byte *)"tessfactor";
                            do {
                              if (iVar15 == 0) break;
                              iVar15 = iVar15 + -1;
                              bVar20 = *pbVar9 == *pbVar13;
                              pbVar9 = pbVar9 + 1;
                              pbVar13 = pbVar13 + 1;
                            } while (bVar20);
                            if (bVar20) {
                              local_48 = 8;
                            }
                            else {
                              local_48 = 10;
                              bVar20 = true;
                              uVar11 = local_48;
                              pbVar9 = local_10;
                              pbVar13 = (byte *)"positiont";
                              do {
                                if (uVar11 == 0) break;
                                uVar11 = uVar11 - 1;
                                bVar20 = *pbVar9 == *pbVar13;
                                pbVar9 = pbVar9 + 1;
                                pbVar13 = pbVar13 + 1;
                              } while (bVar20);
                              if (bVar20) {
                                local_48 = 9;
                              }
                              else {
                                iVar15 = 6;
                                bVar20 = true;
                                pbVar9 = local_10;
                                pbVar13 = (byte *)"color";
                                do {
                                  if (iVar15 == 0) break;
                                  iVar15 = iVar15 + -1;
                                  bVar20 = *pbVar9 == *pbVar13;
                                  pbVar9 = pbVar9 + 1;
                                  pbVar13 = pbVar13 + 1;
                                } while (bVar20);
                                if (!bVar20) {
                                  iVar15 = 4;
                                  bVar20 = true;
                                  pbVar9 = local_10;
                                  pbVar13 = &DAT_005ec9e4;
                                  do {
                                    if (iVar15 == 0) break;
                                    iVar15 = iVar15 + -1;
                                    bVar20 = *pbVar9 == *pbVar13;
                                    pbVar9 = pbVar9 + 1;
                                    pbVar13 = pbVar13 + 1;
                                  } while (bVar20);
                                  if (bVar20) {
                                    local_48 = 0xb;
                                  }
                                  else {
                                    iVar15 = 6;
                                    bVar20 = true;
                                    pbVar9 = local_10;
                                    pbVar13 = (byte *)"depth";
                                    do {
                                      if (iVar15 == 0) break;
                                      iVar15 = iVar15 + -1;
                                      bVar20 = *pbVar9 == *pbVar13;
                                      pbVar9 = pbVar9 + 1;
                                      pbVar13 = pbVar13 + 1;
                                    } while (bVar20);
                                    if (bVar20) {
                                      local_48 = 0xc;
                                    }
                                    else {
                                      iVar15 = 7;
                                      bVar20 = true;
                                      pbVar9 = local_10;
                                      pbVar13 = (byte *)"sample";
                                      do {
                                        if (iVar15 == 0) break;
                                        iVar15 = iVar15 + -1;
                                        bVar20 = *pbVar9 == *pbVar13;
                                        pbVar9 = pbVar9 + 1;
                                        pbVar13 = pbVar13 + 1;
                                      } while (bVar20);
                                      if (!bVar20) goto LAB_0058e228;
                                      local_48 = 0xd;
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            bVar5 = false;
            local_48 = (uVar8 & 0xf) << 0x10 | local_48;
            bVar20 = false;
          }
          else {
            if (!bVar21) goto LAB_0058e228;
            bVar21 = true;
            iVar10 = iVar15;
            pbVar9 = local_10;
            pbVar13 = &DAT_005ec9d0;
            do {
              if (iVar10 == 0) break;
              iVar10 = iVar10 + -1;
              bVar21 = *pbVar9 == *pbVar13;
              pbVar9 = pbVar9 + 1;
              pbVar13 = pbVar13 + 1;
            } while (bVar21);
            if (bVar21) {
              local_48 = 1;
            }
            else {
              bVar21 = true;
              iVar10 = iVar15;
              pbVar9 = local_10;
              pbVar13 = &DAT_005ec9cc;
              do {
                if (iVar10 == 0) break;
                iVar10 = iVar10 + -1;
                bVar21 = *pbVar9 == *pbVar13;
                pbVar9 = pbVar9 + 1;
                pbVar13 = pbVar13 + 1;
              } while (bVar21);
              if (bVar21) {
                local_48 = 2;
              }
              else {
                bVar21 = true;
                iVar10 = iVar15;
                pbVar9 = local_10;
                pbVar13 = &DAT_005ec9c8;
                do {
                  if (iVar10 == 0) break;
                  iVar10 = iVar10 + -1;
                  bVar21 = *pbVar9 == *pbVar13;
                  pbVar9 = pbVar9 + 1;
                  pbVar13 = pbVar13 + 1;
                } while (bVar21);
                if (bVar21) {
                  local_48 = 3;
                }
                else {
                  bVar21 = true;
                  iVar10 = iVar15;
                  pbVar9 = local_10;
                  pbVar13 = &DAT_005ec9c4;
                  do {
                    if (iVar10 == 0) break;
                    iVar10 = iVar10 + -1;
                    bVar21 = *pbVar9 == *pbVar13;
                    pbVar9 = pbVar9 + 1;
                    pbVar13 = pbVar13 + 1;
                  } while (bVar21);
                  if (bVar21) {
                    local_48 = 4;
                  }
                  else {
                    bVar21 = true;
                    iVar10 = iVar15;
                    pbVar9 = local_10;
                    pbVar13 = &DAT_005ec9c0;
                    do {
                      if (iVar10 == 0) break;
                      iVar10 = iVar10 + -1;
                      bVar21 = *pbVar9 == *pbVar13;
                      pbVar9 = pbVar9 + 1;
                      pbVar13 = pbVar13 + 1;
                    } while (bVar21);
                    if (bVar21) {
                      local_48 = 5;
                    }
                    else {
                      bVar21 = true;
                      pbVar9 = local_10;
                      pbVar13 = &DAT_005ec9bc;
                      do {
                        if (iVar15 == 0) break;
                        iVar15 = iVar15 + -1;
                        bVar21 = *pbVar9 == *pbVar13;
                        pbVar9 = pbVar9 + 1;
                        pbVar13 = pbVar13 + 1;
                      } while (bVar21);
                      if (!bVar21) goto LAB_0058e228;
                      local_48 = 6;
                    }
                  }
                }
              }
            }
            bVar21 = false;
          }
        }
      }
LAB_0058e1b0:
      local_20 = (byte *)param_1;
    } while (*(char *)param_1 != '\0');
    if (local_44 == 0x28) {
      if (bVar21) goto LAB_0058e221;
      if (*(int *)(&DAT_005ebf88 + *(int *)((int)this + 0x38) * 4) != -1) {
        local_44 = 0x29;
        local_50 = 0x10c;
        goto LAB_0058e1e8;
      }
    }
    else {
LAB_0058e1e8:
      if (local_44 == 0x2c) {
        if (bVar21) goto LAB_0058e221;
        if (*(int *)(&DAT_005ebfd0 + *(int *)((int)this + 0x38) * 4) == -1) goto LAB_0058e228;
        local_44 = 0x2d;
        local_50 = 0x10c;
      }
      if ((local_44 != 0x5e) || (!bVar21)) {
LAB_0058e221:
        if (!bVar5) goto LAB_0058e22f;
      }
    }
LAB_0058e228:
    local_50 = 0x10d;
  }
  return local_50;
}
