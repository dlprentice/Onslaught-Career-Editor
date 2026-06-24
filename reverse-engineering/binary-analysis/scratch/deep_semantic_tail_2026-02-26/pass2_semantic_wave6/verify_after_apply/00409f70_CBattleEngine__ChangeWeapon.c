/* address: 0x00409f70 */
/* name: CBattleEngine__ChangeWeapon */
/* signature: void __fastcall CBattleEngine__ChangeWeapon(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CBattleEngine__ChangeWeapon(int param_1)

{
  byte bVar1;
  int iVar2;
  char *pcVar3;
  void *pvVar4;
  byte *pbVar5;
  byte *pbVar6;
  int unaff_EDI;
  bool bVar7;
  char local_100 [256];

  if (*(int *)(param_1 + 0x260) == 3) {
    iVar2 = LinkedObjectList__CountFlag9C(*(void **)(param_1 + 0x57c));
  }
  else {
    iVar2 = LinkedObjectList__CountFlag9C_IncludingExtra(*(void **)(param_1 + 0x578));
  }
  if (iVar2 < 2) {
    return;
  }
  *(undefined4 *)(param_1 + 0x588) = 0;
  if (*(int *)(param_1 + 0x260) == 2) {
    CGeneralVolume__Unk_00413eb0(*(void **)(param_1 + 0x578));
  }
  else if (*(int *)(param_1 + 0x260) == 3) {
    CCockpit__Unk_00411e70(*(void **)(param_1 + 0x57c));
  }
  *(undefined4 *)(param_1 + 0x584) = DAT_00672fd0;
  if (*(int *)(param_1 + 0x260) == 3) {
    iVar2 = CGeneralVolume__Unk_004124d0(*(void **)(param_1 + 0x57c));
  }
  else {
    iVar2 = CGeneralVolume__Unk_004145f0(*(void **)(param_1 + 0x578));
  }
  if (iVar2 == 0) {
    return;
  }
  pbVar5 = (byte *)(iVar2 + 7);
  pcVar3 = s_Vulcan_Cannon_006234a0;
  pbVar6 = pbVar5;
  do {
    bVar1 = *pcVar3;
    bVar7 = bVar1 < *pbVar6;
    if (bVar1 != *pbVar6) {
LAB_0040a03e:
      iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
      goto LAB_0040a043;
    }
    if (bVar1 == 0) break;
    bVar1 = pcVar3[1];
    bVar7 = bVar1 < pbVar6[1];
    if (bVar1 != pbVar6[1]) goto LAB_0040a03e;
    pcVar3 = pcVar3 + 2;
    pbVar6 = pbVar6 + 2;
  } while (bVar1 != 0);
  iVar2 = 0;
LAB_0040a043:
  if (iVar2 == 0) {
    sprintf(local_100,s_hud__s_00623314);
  }
  else {
    pcVar3 = s_Grenade_00623484;
    pbVar6 = pbVar5;
    do {
      bVar1 = *pcVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_0040a094:
        iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040a099;
      }
      if (bVar1 == 0) break;
      bVar1 = pcVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_0040a094;
      pcVar3 = pcVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar2 = 0;
LAB_0040a099:
    if (iVar2 == 0) {
      sprintf(local_100,s_hud__s_00623314);
    }
    else {
      pcVar3 = s_Torpedo_00623464;
      pbVar6 = pbVar5;
      do {
        bVar1 = *pcVar3;
        bVar7 = bVar1 < *pbVar6;
        if (bVar1 != *pbVar6) {
LAB_0040a0ea:
          iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
          goto LAB_0040a0ef;
        }
        if (bVar1 == 0) break;
        bVar1 = pcVar3[1];
        bVar7 = bVar1 < pbVar6[1];
        if (bVar1 != pbVar6[1]) goto LAB_0040a0ea;
        pcVar3 = pcVar3 + 2;
        pbVar6 = pbVar6 + 2;
      } while (bVar1 != 0);
      iVar2 = 0;
LAB_0040a0ef:
      if (iVar2 == 0) {
        sprintf(local_100,s_hud__s_00623314);
      }
      else {
        pcVar3 = s_Blaster_00623444;
        pbVar6 = pbVar5;
        do {
          bVar1 = *pcVar3;
          bVar7 = bVar1 < *pbVar6;
          if (bVar1 != *pbVar6) {
LAB_0040a140:
            iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
            goto LAB_0040a145;
          }
          if (bVar1 == 0) break;
          bVar1 = pcVar3[1];
          bVar7 = bVar1 < pbVar6[1];
          if (bVar1 != pbVar6[1]) goto LAB_0040a140;
          pcVar3 = pcVar3 + 2;
          pbVar6 = pbVar6 + 2;
        } while (bVar1 != 0);
        iVar2 = 0;
LAB_0040a145:
        if (iVar2 == 0) {
          sprintf(local_100,s_hud__s_00623314);
        }
        else {
          pcVar3 = s_Flux_Pod_0062342c;
          pbVar6 = pbVar5;
          do {
            bVar1 = *pcVar3;
            bVar7 = bVar1 < *pbVar6;
            if (bVar1 != *pbVar6) {
LAB_0040a196:
              iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
              goto LAB_0040a19b;
            }
            if (bVar1 == 0) break;
            bVar1 = pcVar3[1];
            bVar7 = bVar1 < pbVar6[1];
            if (bVar1 != pbVar6[1]) goto LAB_0040a196;
            pcVar3 = pcVar3 + 2;
            pbVar6 = pbVar6 + 2;
          } while (bVar1 != 0);
          iVar2 = 0;
LAB_0040a19b:
          if (iVar2 == 0) {
            sprintf(local_100,s_hud__s_00623314);
          }
          else {
            pcVar3 = s_Micro_Missile_00623408;
            pbVar6 = pbVar5;
            do {
              bVar1 = *pcVar3;
              bVar7 = bVar1 < *pbVar6;
              if (bVar1 != *pbVar6) {
LAB_0040a1ec:
                iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
                goto LAB_0040a1f1;
              }
              if (bVar1 == 0) break;
              bVar1 = pcVar3[1];
              bVar7 = bVar1 < pbVar6[1];
              if (bVar1 != pbVar6[1]) goto LAB_0040a1ec;
              pcVar3 = pcVar3 + 2;
              pbVar6 = pbVar6 + 2;
            } while (bVar1 != 0);
            iVar2 = 0;
LAB_0040a1f1:
            if (iVar2 == 0) {
              sprintf(local_100,s_hud__s_00623314);
            }
            else {
              pcVar3 = s_Spread_Bomb_006233e8;
              pbVar6 = pbVar5;
              do {
                bVar1 = *pcVar3;
                bVar7 = bVar1 < *pbVar6;
                if (bVar1 != *pbVar6) {
LAB_0040a23f:
                  iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
                  goto LAB_0040a244;
                }
                if (bVar1 == 0) break;
                bVar1 = pcVar3[1];
                bVar7 = bVar1 < pbVar6[1];
                if (bVar1 != pbVar6[1]) goto LAB_0040a23f;
                pcVar3 = pcVar3 + 2;
                pbVar6 = pbVar6 + 2;
              } while (bVar1 != 0);
              iVar2 = 0;
LAB_0040a244:
              if (iVar2 != 0) goto LAB_0040a29e;
              sprintf(local_100,s_hud__s_00623314);
            }
          }
        }
      }
    }
  }
  pvVar4 = (void *)CBattleEngine__Helper_004e1910(&DAT_00896988,(int)local_100,0,unaff_EDI);
  CMonitor__Helper_004e1940(&DAT_00896988,pvVar4,(void *)param_1);
LAB_0040a29e:
  pcVar3 = s_Rail_Gun_006233cc;
  pbVar6 = pbVar5;
  if (*(int *)(param_1 + 0x2fc) == 0) {
    do {
      bVar1 = *pcVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_0040a497:
        iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040a49c;
      }
      if (bVar1 == 0) break;
      bVar1 = pcVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_0040a497;
      pcVar3 = pcVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar2 = 0;
LAB_0040a49c:
    if (iVar2 == 0) {
      CGeneralVolume__Unk_0040d5f0(param_1);
      return;
    }
    pcVar3 = s_Beam_Laser_006233a8;
    pbVar6 = pbVar5;
    do {
      bVar1 = *pcVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_0040a4e6:
        iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040a4eb;
      }
      if (bVar1 == 0) break;
      bVar1 = pcVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_0040a4e6;
      pcVar3 = pcVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar2 = 0;
LAB_0040a4eb:
    if (iVar2 == 0) {
      CGeneralVolume__Unk_0040d5f0(param_1);
      return;
    }
    pcVar3 = s_Plasma_Cannon_0062337c;
    do {
      bVar1 = *pcVar3;
      bVar7 = bVar1 < *pbVar5;
      if (bVar1 != *pbVar5) {
LAB_0040a535:
        iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040a53a;
      }
      if (bVar1 == 0) break;
      bVar1 = pcVar3[1];
      bVar7 = bVar1 < pbVar5[1];
      if (bVar1 != pbVar5[1]) goto LAB_0040a535;
      pcVar3 = pcVar3 + 2;
      pbVar5 = pbVar5 + 2;
    } while (bVar1 != 0);
    iVar2 = 0;
LAB_0040a53a:
    if (iVar2 == 0) {
      CGeneralVolume__Unk_0040d5f0(param_1);
    }
  }
  else {
    do {
      bVar1 = *pcVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_0040a2d7:
        iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040a2dc;
      }
      if (bVar1 == 0) break;
      bVar1 = pcVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_0040a2d7;
      pcVar3 = pcVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar2 = 0;
LAB_0040a2dc:
    if (iVar2 == 0) {
      sprintf(local_100,s_hud__s_00623314);
      pvVar4 = (void *)CBattleEngine__Helper_004e1910(&DAT_00896988,(int)local_100,0,unaff_EDI);
      CMonitor__Helper_004e1940(&DAT_00896988,pvVar4,(void *)param_1);
      return;
    }
    pcVar3 = s_Beam_Laser_006233a8;
    pbVar6 = pbVar5;
    do {
      bVar1 = *pcVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_0040a36c:
        iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040a371;
      }
      if (bVar1 == 0) break;
      bVar1 = pcVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_0040a36c;
      pcVar3 = pcVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar2 = 0;
LAB_0040a371:
    if (iVar2 == 0) {
      sprintf(local_100,s_hud__s_00623314);
      pvVar4 = (void *)CBattleEngine__Helper_004e1910(&DAT_00896988,(int)local_100,0,unaff_EDI);
      CMonitor__Helper_004e1940(&DAT_00896988,pvVar4,(void *)param_1);
      return;
    }
    pcVar3 = s_Plasma_Cannon_0062337c;
    do {
      bVar1 = *pcVar3;
      bVar7 = bVar1 < *pbVar5;
      if (bVar1 != *pbVar5) {
LAB_0040a401:
        iVar2 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040a406;
      }
      if (bVar1 == 0) break;
      bVar1 = pcVar3[1];
      bVar7 = bVar1 < pbVar5[1];
      if (bVar1 != pbVar5[1]) goto LAB_0040a401;
      pcVar3 = pcVar3 + 2;
      pbVar5 = pbVar5 + 2;
    } while (bVar1 != 0);
    iVar2 = 0;
LAB_0040a406:
    if (iVar2 == 0) {
      sprintf(local_100,s_hud__s_00623314);
      pvVar4 = (void *)CBattleEngine__Helper_004e1910(&DAT_00896988,(int)local_100,0,unaff_EDI);
      CMonitor__Helper_004e1940(&DAT_00896988,pvVar4,(void *)param_1);
      return;
    }
  }
  return;
}
