/* address: 0x004541e0 */
/* name: Controls__RemapKey */
/* signature: void __cdecl Controls__RemapKey(int action_code, int key_code) */


/* High-level control remap handler.
   Uses Controls__DispatchRemap to translate action_code into (entry_id, binding_type) and updates
   the persisted controls/options entry table. Calls Controls__ClearDuplicateBinding to avoid
   conflicts, and triggers Controls__ApplyPreset(0) to refresh mappings.
   Uses globals DAT_00677870 / DAT_00677874 as remap state. */

void __cdecl Controls__RemapKey(int action_code,int key_code)

{
  int iVar1;
  int iVar2;
  short sVar3;
  short sVar4;
  undefined4 *puVar5;
  short sVar6;
  uint uVar7;
  int iVar8;
  int *piVar9;
  uint uVar10;
  int iVar11;
  int local_8;

  iVar8 = key_code;
  sVar4 = g_ControlRemapVkScanPacked._2_2_;
  iVar11 = g_ControlRemapBindingType;
  uVar7 = 0xffffffff;
  do {
    sVar6 = (short)uVar7;
    uVar10 = uVar7;
    if (action_code == 0x40) {
      if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
         (g_ControlRemapBindingType == 5)) {
LAB_004544f0:
        sVar4 = sVar6 + -1;
        g_ControlRemapBindingType = 5;
        g_ControlRemapVkScanPacked._2_2_ = sVar4;
        Controls__ClearDuplicateBinding(key_code,sVar4,5);
        Controls__DispatchRemap(0x40,key_code,&LAB_004540c0);
        Controls__ApplyPreset(0);
        iVar11 = 4;
        g_ControlRemapBindingType = 4;
        g_ControlRemapVkScanPacked._2_2_ = sVar4;
        Controls__ClearDuplicateBinding(key_code,sVar4,4);
        Controls__DispatchRemap(0x41,key_code,&LAB_004540c0);
        Controls__ApplyPreset(0);
        g_ControlRemapBindingType = 5;
        iVar1 = 5;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
LAB_00454569:
        Controls__ClearDuplicateBinding(key_code,(short)uVar10,iVar1);
        Controls__DispatchRemap(0x42,key_code,&LAB_004540c0);
        Controls__ApplyPreset(0);
        g_ControlRemapVkScanPacked._2_2_ = (short)uVar7;
        g_ControlRemapBindingType = iVar11;
      }
      else {
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 5)) {
LAB_004545c4:
          iVar11 = 5;
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          Controls__ClearDuplicateBinding(key_code,sVar6,5);
          Controls__DispatchRemap(0x40,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          Controls__ClearDuplicateBinding(key_code,sVar6,4);
          Controls__DispatchRemap(0x41,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          uVar7 = uVar7 - 1;
          iVar1 = 4;
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = (short)uVar7;
          uVar10 = uVar7 & 0xffff;
          goto LAB_00454569;
        }
        if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
           (g_ControlRemapBindingType == 4)) {
LAB_00454636:
          sVar4 = sVar6 + -1;
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar4;
          Controls__ClearDuplicateBinding(key_code,sVar4,4);
          Controls__DispatchRemap(0x40,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          iVar11 = 5;
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar4;
          Controls__ClearDuplicateBinding(key_code,sVar4,5);
          Controls__DispatchRemap(0x41,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 4;
          iVar1 = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          goto LAB_00454569;
        }
        if ((g_ControlRemapVkScanPacked._2_2_ != sVar6) || (g_ControlRemapBindingType != 4))
        goto LAB_00454450;
LAB_004546b3:
        g_ControlRemapBindingType = 4;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
        Controls__ClearDuplicateBinding(key_code,sVar6,4);
        Controls__DispatchRemap(0x40,key_code,&LAB_004540c0);
        Controls__ApplyPreset(0);
        g_ControlRemapBindingType = 5;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
        Controls__ClearDuplicateBinding(key_code,sVar6,5);
        Controls__DispatchRemap(0x41,key_code,&LAB_004540c0);
        Controls__ApplyPreset(0);
        sVar6 = sVar6 + -1;
        g_ControlRemapBindingType = 5;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
        Controls__ClearDuplicateBinding(key_code,sVar6,5);
        Controls__DispatchRemap(0x42,key_code,&LAB_004540c0);
        Controls__ApplyPreset(0);
        g_ControlRemapBindingType = 4;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
      }
      Controls__ClearDuplicateBinding
                (key_code,g_ControlRemapVkScanPacked._2_2_,g_ControlRemapBindingType);
      iVar11 = 0x43;
      goto LAB_004545a3;
    }
    if (action_code == 0x41) {
      if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
         (g_ControlRemapBindingType == 4)) goto LAB_004544f0;
      if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 4))
      goto LAB_004545c4;
      sVar3 = sVar6;
      if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
         (g_ControlRemapBindingType == 5)) goto LAB_00454636;
joined_r0x00454311:
      if ((g_ControlRemapVkScanPacked._2_2_ == sVar3) && (g_ControlRemapBindingType == 5))
      goto LAB_004546b3;
    }
    else {
      if (action_code == 0x42) {
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 5))
        goto LAB_004544f0;
        sVar3 = sVar6 + -1;
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar3) && (g_ControlRemapBindingType == 4))
        goto LAB_004545c4;
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 4))
        goto LAB_00454636;
        goto joined_r0x00454311;
      }
      if (action_code == 0x43) {
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 4))
        goto LAB_004544f0;
        if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
           (g_ControlRemapBindingType == 5)) goto LAB_004545c4;
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 5))
        goto LAB_00454636;
        if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
           (g_ControlRemapBindingType == 4)) goto LAB_004546b3;
      }
      else if (action_code == 0x3b) {
        if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
           (g_ControlRemapBindingType == 5)) {
LAB_00454750:
          sVar4 = sVar6 + -1;
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar4;
          Controls__ClearDuplicateBinding(key_code,sVar4,5);
          Controls__DispatchRemap(0x3b,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar4;
          Controls__ClearDuplicateBinding(key_code,sVar4,4);
          Controls__DispatchRemap(0x3c,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          Controls__ClearDuplicateBinding(key_code,sVar6,5);
          Controls__DispatchRemap(0x3d,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          if (DAT_008892dc != -1) {
            action_code = (int)&DAT_008892dc;
            do {
              if (*(char *)(action_code + -4) != '\0') {
                piVar9 = (int *)(action_code + 4);
                key_code = 2;
                do {
                  if ((*piVar9 == iVar8) && ((short)piVar9[2] == sVar6)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(4);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  key_code = key_code + -1;
                } while (key_code != 0);
              }
              piVar9 = (int *)(action_code + 0x20);
              action_code = action_code + 0x20;
            } while (*piVar9 != -1);
          }
          goto LAB_00454dc8;
        }
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 5)) {
LAB_0045486d:
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          Controls__ClearDuplicateBinding(key_code,sVar6,5);
          Controls__DispatchRemap(0x3b,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          if (DAT_008892dc != -1) {
            action_code = (int)&DAT_008892dc;
            do {
              if (*(char *)(action_code + -4) != '\0') {
                piVar9 = (int *)(action_code + 4);
                key_code = 2;
                do {
                  if ((*piVar9 == iVar8) && ((short)piVar9[2] == sVar6)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(4);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  key_code = key_code + -1;
                } while (key_code != 0);
              }
              piVar9 = (int *)(action_code + 0x20);
              action_code = action_code + 0x20;
            } while (*piVar9 != -1);
          }
          Controls__DispatchRemap(0x3c,iVar8,&LAB_004540c0);
          Controls__ApplyPreset(0);
          sVar6 = sVar6 + -1;
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          if (DAT_008892dc != -1) {
            puVar5 = &DAT_008892dc;
            do {
              if (*(char *)(puVar5 + -1) != '\0') {
                piVar9 = puVar5 + 1;
                action_code = 2;
                do {
                  if ((*piVar9 == iVar8) && ((short)piVar9[2] == sVar6)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(4);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  action_code = action_code + -1;
                } while (action_code != 0);
              }
              piVar9 = puVar5 + 8;
              puVar5 = puVar5 + 8;
            } while (*piVar9 != -1);
          }
          Controls__DispatchRemap(0x3d,iVar8,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          Controls__ClearDuplicateBinding(iVar8,sVar6,5);
          iVar11 = 0x3e;
LAB_004545a3:
          Controls__DispatchRemap(iVar11,iVar8,&LAB_004540c0);
          Controls__ApplyPreset(0);
          Controls__ApplyPreset(0);
          return;
        }
        sVar3 = sVar6;
        if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
           (g_ControlRemapBindingType == 4)) goto LAB_004549ff;
joined_r0x004543fc:
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar3) && (g_ControlRemapBindingType == 4)) {
LAB_00454bf1:
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          if (DAT_008892dc != -1) {
            puVar5 = &DAT_008892dc;
            do {
              if (*(char *)(puVar5 + -1) != '\0') {
                piVar9 = puVar5 + 1;
                action_code = 2;
                do {
                  if ((*piVar9 == key_code) && ((short)piVar9[2] == sVar6)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(4);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  action_code = action_code + -1;
                } while (action_code != 0);
              }
              piVar9 = puVar5 + 8;
              puVar5 = puVar5 + 8;
            } while (*piVar9 != -1);
          }
          Controls__DispatchRemap(0x3b,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          if (DAT_008892dc != -1) {
            puVar5 = &DAT_008892dc;
            do {
              if (*(char *)(puVar5 + -1) != '\0') {
                piVar9 = puVar5 + 1;
                action_code = 2;
                do {
                  if ((*piVar9 == key_code) && ((short)piVar9[2] == sVar6)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(5);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  action_code = action_code + -1;
                } while (action_code != 0);
              }
              piVar9 = puVar5 + 8;
              puVar5 = puVar5 + 8;
            } while (*piVar9 != -1);
          }
          Controls__DispatchRemap(0x3c,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          sVar6 = sVar6 + -1;
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          Controls__ClearDuplicateBinding(key_code,sVar6,5);
          Controls__DispatchRemap(0x3d,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          if (DAT_008892dc != -1) {
            puVar5 = &DAT_008892dc;
            do {
              if (*(char *)(puVar5 + -1) != '\0') {
                piVar9 = puVar5 + 1;
                iVar11 = 2;
                do {
                  if ((*piVar9 == key_code) && ((short)piVar9[2] == sVar6)) {
                    iVar1 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar2 = Controls__GetDeviceCategory(4);
                    if (iVar2 == iVar1) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  iVar11 = iVar11 + -1;
                } while (iVar11 != 0);
              }
              piVar9 = puVar5 + 8;
              puVar5 = puVar5 + 8;
            } while (*piVar9 != -1);
          }
          goto LAB_00454dc8;
        }
      }
      else {
        if (action_code != 0x3c) {
          if (action_code == 0x3d) {
            if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 5))
            goto LAB_00454750;
            sVar3 = sVar6 + -1;
            if ((g_ControlRemapVkScanPacked._2_2_ == sVar3) && (g_ControlRemapBindingType == 4))
            goto LAB_0045486d;
            if ((g_ControlRemapVkScanPacked._2_2_ != sVar6) || (g_ControlRemapBindingType != 4))
            goto joined_r0x00454419;
          }
          else {
            if (action_code != 0x3e) goto LAB_00454450;
            if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 4))
            goto LAB_00454750;
            sVar3 = sVar6 + -1;
            if ((g_ControlRemapVkScanPacked._2_2_ == sVar3) && (g_ControlRemapBindingType == 5))
            goto LAB_0045486d;
            if ((g_ControlRemapVkScanPacked._2_2_ != sVar6) || (g_ControlRemapBindingType != 5))
            goto joined_r0x004543fc;
          }
LAB_004549ff:
          sVar4 = sVar6 + -1;
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar4;
          if (DAT_008892dc != -1) {
            puVar5 = &DAT_008892dc;
            do {
              if (*(char *)(puVar5 + -1) != '\0') {
                piVar9 = puVar5 + 1;
                local_8 = 2;
                do {
                  if ((*piVar9 == key_code) && ((short)piVar9[2] == sVar4)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(4);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  local_8 = local_8 + -1;
                } while (local_8 != 0);
              }
              piVar9 = puVar5 + 8;
              puVar5 = puVar5 + 8;
            } while (*piVar9 != -1);
          }
          Controls__DispatchRemap(0x3b,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          sVar4 = sVar6 + -1;
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar4;
          if (DAT_008892dc != -1) {
            puVar5 = &DAT_008892dc;
            do {
              if (*(char *)(puVar5 + -1) != '\0') {
                piVar9 = puVar5 + 1;
                local_8 = 2;
                do {
                  if ((*piVar9 == key_code) && ((short)piVar9[2] == sVar4)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(5);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  local_8 = local_8 + -1;
                } while (local_8 != 0);
              }
              piVar9 = puVar5 + 8;
              puVar5 = puVar5 + 8;
            } while (*piVar9 != -1);
          }
          Controls__DispatchRemap(0x3c,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 4;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          Controls__ClearDuplicateBinding(key_code,sVar6,4);
          Controls__DispatchRemap(0x3d,key_code,&LAB_004540c0);
          Controls__ApplyPreset(0);
          g_ControlRemapBindingType = 5;
          g_ControlRemapVkScanPacked._2_2_ = sVar6;
          if (DAT_008892dc != -1) {
            puVar5 = &DAT_008892dc;
            do {
              if (*(char *)(puVar5 + -1) != '\0') {
                piVar9 = puVar5 + 1;
                action_code = 2;
                do {
                  if ((*piVar9 == key_code) && ((short)piVar9[2] == sVar6)) {
                    iVar11 = Controls__GetDeviceCategory(piVar9[1]);
                    iVar1 = Controls__GetDeviceCategory(5);
                    if (iVar1 == iVar11) {
                      *piVar9 = -1;
                    }
                  }
                  piVar9 = piVar9 + 3;
                  action_code = action_code + -1;
                } while (action_code != 0);
              }
              piVar9 = puVar5 + 8;
              puVar5 = puVar5 + 8;
            } while (*piVar9 != -1);
          }
LAB_00454dc8:
          Controls__DispatchRemap(0x3e,iVar8,&LAB_004540c0);
          Controls__ApplyPreset(0);
          Controls__ApplyPreset(0);
          return;
        }
        if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
           (g_ControlRemapBindingType == 4)) goto LAB_00454750;
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar6) && (g_ControlRemapBindingType == 4))
        goto LAB_0045486d;
        sVar3 = sVar6;
        if ((g_ControlRemapVkScanPacked._2_2_ == (short)(sVar6 + -1)) &&
           (g_ControlRemapBindingType == 5)) goto LAB_004549ff;
joined_r0x00454419:
        if ((g_ControlRemapVkScanPacked._2_2_ == sVar3) && (g_ControlRemapBindingType == 5))
        goto LAB_00454bf1;
      }
    }
LAB_00454450:
    uVar7 = uVar7 - 2;
    if ((int)uVar7 < -5) {
      if (DAT_008892dc != -1) {
        puVar5 = &DAT_008892dc;
        do {
          if (*(char *)(puVar5 + -1) != '\0') {
            piVar9 = puVar5 + 1;
            iVar8 = 2;
            do {
              if ((*piVar9 == key_code) && ((short)piVar9[2] == sVar4)) {
                iVar1 = Controls__GetDeviceCategory(piVar9[1]);
                iVar2 = Controls__GetDeviceCategory(iVar11);
                if (iVar2 == iVar1) {
                  *piVar9 = -1;
                }
              }
              piVar9 = piVar9 + 3;
              iVar8 = iVar8 + -1;
            } while (iVar8 != 0);
          }
          piVar9 = puVar5 + 8;
          puVar5 = puVar5 + 8;
        } while (*piVar9 != -1);
      }
      Controls__DispatchRemap(action_code,key_code,&LAB_004540c0);
      Controls__ApplyPreset(0);
      return;
    }
  } while( true );
}
