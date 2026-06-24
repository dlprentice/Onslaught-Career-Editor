/* address: 0x004e1b20 */
/* name: CSoundManager__UpdateStatus */
/* signature: void __fastcall CSoundManager__UpdateStatus(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Source-aligned with CSoundManager::UpdateStatus(). Refreshes camera pos/orientation from
   GAME.GetCamera(0), sorts sound events, calls SOUND.UpdateGlobals(), computes time delta via
   PLATFORM__GetSysTimeFloat, updates each sound event (position/fade/pitch/debug marker/owner
   reader cleanup), and services paused/frozen behavior. */

void __fastcall CSoundManager__UpdateStatus(void *this)

{
  float fVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  bool bVar6;
  int *sound_event;
  int *piVar7;
  undefined4 *puVar8;
  void *pvVar9;
  int iVar10;
  int iVar11;
  undefined4 uVar12;
  undefined4 *puVar13;
  float fVar14;
  float fVar15;
  double dVar16;
  int iStack_a0;
  int iStack_98;
  undefined4 uStack_80;
  undefined4 uStack_60;
  int iStack_50;
  float local_4c;
  float fStack_48;
  float afStack_44 [14];
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d4c1e;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  piVar7 = CGame__GetCamera(&DAT_008a9a98,0);
  if (piVar7 == (int *)0x0) {
    *(undefined4 *)((int)this + 0x38) = DAT_0083cfd8;
    *(undefined4 *)((int)this + 0x3c) = DAT_0083cfdc;
    *(undefined4 *)((int)this + 0x40) = DAT_0083cfe0;
    *(undefined4 *)((int)this + 0x44) = DAT_0083cfe4;
    puVar8 = &DAT_0083cfa8;
    puVar13 = (undefined4 *)((int)this + 0x58);
    for (iVar11 = 0xc; iVar11 != 0; iVar11 = iVar11 + -1) {
      *puVar13 = *puVar8;
      puVar8 = puVar8 + 1;
      puVar13 = puVar13 + 1;
    }
    *(undefined4 *)((int)this + 0x48) = DAT_0083cfd8;
    *(undefined4 *)((int)this + 0x4c) = DAT_0083cfdc;
    *(undefined4 *)((int)this + 0x50) = DAT_0083cfe0;
    *(undefined4 *)((int)this + 0x54) = DAT_0083cfe4;
  }
  else {
    puVar8 = (undefined4 *)(**(code **)*piVar7)(&local_4c);
    *(undefined4 *)((int)this + 0x38) = *puVar8;
    *(undefined4 *)((int)this + 0x3c) = puVar8[1];
    *(undefined4 *)((int)this + 0x40) = puVar8[2];
    *(undefined4 *)((int)this + 0x44) = puVar8[3];
    puVar8 = (undefined4 *)(**(code **)(*piVar7 + 8))(&iStack_50);
    *(undefined4 *)((int)this + 0x48) = *puVar8;
    *(undefined4 *)((int)this + 0x4c) = puVar8[1];
    *(undefined4 *)((int)this + 0x50) = puVar8[2];
    *(undefined4 *)((int)this + 0x54) = puVar8[3];
    puVar8 = (undefined4 *)(**(code **)(*piVar7 + 4))(afStack_44);
    puVar13 = (undefined4 *)((int)this + 0x58);
    for (iVar11 = 0xc; iVar11 != 0; iVar11 = iVar11 + -1) {
      *puVar13 = *puVar8;
      puVar8 = puVar8 + 1;
      puVar13 = puVar13 + 1;
    }
  }
  CSoundManager__Unk_004e1040((int)this);
  CSoundManager__UpdateListener3D(&DAT_00896988);
  fVar14 = PLATFORM__GetSysTimeFloat();
  fVar1 = *(float *)((int)this + 0x14);
  fVar15 = PLATFORM__GetSysTimeFloat();
  *(float *)((int)this + 0x14) = fVar15;
  piVar7 = *(int **)((int)this + 0xc);
  do {
    sound_event = piVar7;
    if (sound_event == (int *)0x0) {
      CSoundManager__CommitListener(&DAT_00896988);
      ExceptionList = pvStack_c;
      return;
    }
    if (sound_event[0x21] == 0) {
      sound_event[0xb] = (int)((fVar14 - fVar1) + (float)sound_event[0xb]);
    }
    if (*(int *)((int)this + 0x1c) == 0) {
      CSoundManager__Unk_004e1360(sound_event,0);
    }
    if (*(int *)((int)this + 0x18) == 0) {
      pvVar9 = (void *)sound_event[0x1c];
      if (pvVar9 != (void *)0x0) {
        CSoundManager__Helper_00442380(pvVar9);
        OID__FreeObject(pvVar9);
        sound_event[0x1c] = 0;
      }
    }
    else {
      if (sound_event[0x1c] == 0) {
        pvVar9 = (void *)OID__AllocObject(0x198,0,&DAT_00662b2c,0);
        uStack_4 = 0;
        if (pvVar9 == (void *)0x0) {
          iVar11 = 0;
        }
        else {
          iVar11 = CSoundManager__Helper_004422d0(pvVar9);
        }
        sound_event[0x1c] = iVar11;
        uStack_4 = 0xffffffff;
        *(undefined4 *)(iVar11 + 0x94) = 0xffff0000;
      }
      if ((((float)sound_event[0x11] == *(float *)((int)this + 0x38)) &&
          ((float)sound_event[0x12] == *(float *)((int)this + 0x3c))) &&
         ((float)sound_event[0x13] == *(float *)((int)this + 0x40))) {
        iVar11 = sound_event[0x1c];
        puVar8 = (undefined4 *)(iVar11 + 0x84);
        *puVar8 = 0;
        *(undefined4 *)(iVar11 + 0x88) = 0;
        *(undefined4 *)(iVar11 + 0x8c) = 0;
        uVar12 = uStack_60;
      }
      else {
        iVar11 = sound_event[0x1c];
        puVar8 = (undefined4 *)(iVar11 + 0x84);
        *puVar8 = 0x3dcccccd;
        *(undefined4 *)(iVar11 + 0x88) = 0x3dcccccd;
        *(undefined4 *)(iVar11 + 0x8c) = 0x3dcccccd;
        uVar12 = uStack_80;
      }
      puVar8[3] = uVar12;
      iVar11 = sound_event[0x1c];
      iVar10 = sound_event[0x12];
      iVar2 = sound_event[0x13];
      iVar3 = sound_event[0x14];
      *(int *)(iVar11 + 4) = sound_event[0x11];
      *(int *)(iVar11 + 8) = iVar10;
      *(int *)(iVar11 + 0xc) = iVar2;
      *(int *)(iVar11 + 0x10) = iVar3;
      iVar11 = sound_event[0x1c];
      if (sound_event[3] == 0) {
        _strncpy((char *)(iVar11 + 0x98),s_No_sample__006324f8,0xff);
        *(undefined1 *)(iVar11 + 0x197) = 0;
      }
      else {
        _strncpy((char *)(iVar11 + 0x98),(char *)(sound_event[3] + 8),0xff);
        *(undefined1 *)(iVar11 + 0x197) = 0;
      }
    }
    if (((float)sound_event[0xb] <= _DAT_005d85d8) || ((char)sound_event[2] != '\0')) {
      if (sound_event[0x21] == 0) {
        iVar11 = sound_event[0x10];
        if (iVar11 < 1) {
          sound_event[0xe] = sound_event[0xf];
        }
        else {
          sound_event[0x10] = iVar11 + -1;
          sound_event[0xe] =
               (int)(((float)sound_event[0xf] - (float)sound_event[0xe]) / (float)iVar11 +
                    (float)sound_event[0xe]);
        }
        if ((float)sound_event[9] != _DAT_005d856c) {
          sound_event[8] = (int)((float)sound_event[9] + (float)sound_event[8]);
          if ((float)sound_event[9] <= _DAT_005d856c) {
            if ((float)sound_event[8] < (float)sound_event[10]) {
              bVar6 = (float)sound_event[10] == _DAT_005d856c;
              sound_event[9] = 0;
              sound_event[8] = sound_event[10];
              if (bVar6) {
                if ((sound_event[0x1f] == 1) && ((int *)*sound_event != (int *)0x0)) {
                  (**(code **)(*(int *)*sound_event + 0x18))(sound_event);
                }
                if (-1 < sound_event[1]) {
                  CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event);
                }
                *(undefined1 *)(sound_event + 2) = 0;
                CGenericActiveReader__SetReader(sound_event,(void *)0x0);
              }
            }
          }
          else if ((float)sound_event[10] < (float)sound_event[8]) {
            sound_event[9] = 0;
            sound_event[8] = sound_event[10];
          }
          if ((float)sound_event[8] != _DAT_005d856c) {
            if (sound_event[4] == 0) {
              iStack_98 = 0x7f;
            }
            else {
              fVar15 = (float)sound_event[0x11];
              fVar4 = (float)sound_event[0x12];
              fVar5 = (float)sound_event[0x13];
              iStack_50 = sound_event[0x14];
              CGame__GetCamera(&DAT_008a9a98,0);
              local_4c = -fVar15;
              fStack_48 = -fVar4;
              afStack_44[0] = -fVar5;
              dVar16 = SQRT__Wrapper_004026b0(&local_4c);
              dVar16 = (double)_DAT_005d85d0 - dVar16;
              if (dVar16 <= (double)_DAT_005d85d0) {
                if (dVar16 < (double)_DAT_005d856c) {
                  dVar16 = (double)_DAT_005d856c;
                }
              }
              else {
                dVar16 = (double)_DAT_005d85d0;
              }
              iStack_98 = (int)(longlong)
                               ROUND(dVar16 * (double)_DAT_005db020 * (double)_DAT_005d8cc8);
            }
            fVar15 = (float)sound_event[7] * (float)sound_event[8];
            if (sound_event[5] == 1) {
              iStack_a0 = (int)(longlong)
                               ROUND(*(float *)((int)this + 0x24) * *(float *)((int)this + 0x20) *
                                     fVar15 * _DAT_005dbc4c);
            }
            else {
              iStack_a0 = (int)(longlong)
                               ROUND(*(float *)((int)this + 0x28) * *(float *)((int)this + 0x20) *
                                     fVar15 * _DAT_005dbc4c);
            }
            iStack_a0 = iStack_a0 * 200;
            if (10000 < iStack_a0) {
              iStack_a0 = 10000;
            }
            iVar11 = (iStack_a0 + -10000) / 2;
            if (iVar11 < -10000) {
              iVar11 = -10000;
            }
            if (sound_event[5] == 1) {
              iStack_a0 = (int)(longlong)
                               ROUND((float)iStack_98 * *(float *)((int)this + 0x24) *
                                     *(float *)((int)this + 0x20) * fVar15);
            }
            else {
              iStack_a0 = (int)(longlong)
                               ROUND((float)iStack_98 * *(float *)((int)this + 0x28) *
                                     *(float *)((int)this + 0x20) * fVar15);
            }
            iStack_a0 = iStack_a0 * 200;
            if (10000 < iStack_a0) {
              iStack_a0 = 10000;
            }
            iVar10 = (iStack_a0 + -10000) / 2;
            if (iVar10 < -10000) {
              iVar10 = -10000;
            }
            sound_event[0x1a] = iVar10;
            sound_event[0x19] = iVar11;
            if (sound_event[4] == 0) {
              sound_event[0x1a] = iVar11;
            }
          }
        }
        iVar11 = sound_event[4];
        if (((iVar11 == 2) || (iVar11 == 3)) || (iVar11 == 1)) {
          piVar7 = (int *)*sound_event;
          if ((piVar7 == (int *)0x0) || (sound_event[0x20] == 1)) {
            if (iVar11 == 2) {
              if ((sound_event[0x1f] == 1) && (piVar7 != (int *)0x0)) {
                (**(code **)(*piVar7 + 0x18))(sound_event);
              }
              if (-1 < sound_event[1]) {
                CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event);
              }
              *(undefined1 *)(sound_event + 2) = 0;
              goto LAB_004e2212;
            }
          }
          else {
            fVar15 = (float)sound_event[0x11];
            fVar4 = (float)sound_event[0x12];
            fVar5 = (float)sound_event[0x13];
            CGame__GetCamera(&DAT_008a9a98,0);
            fVar15 = _DAT_005d85d0 - SQRT(-fVar4 * -fVar4 + -fVar5 * -fVar5 + -fVar15 * -fVar15);
            fVar4 = _DAT_005d85d0;
            if ((fVar15 <= _DAT_005d85d0) && (fVar4 = fVar15, fVar15 < _DAT_005d856c)) {
              fVar4 = _DAT_005d856c;
            }
            iStack_a0 = (int)(longlong)ROUND(fVar4 * _DAT_005db020 * _DAT_005d8cc8);
            iVar11 = iStack_a0;
            fVar15 = (float)sound_event[8] * (float)sound_event[7];
            if (sound_event[5] == 1) {
              iStack_a0 = (int)(longlong)
                               ROUND(*(float *)((int)this + 0x24) * *(float *)((int)this + 0x20) *
                                     fVar15 * _DAT_005dbc4c);
            }
            else {
              iStack_a0 = (int)(longlong)
                               ROUND(*(float *)((int)this + 0x28) * *(float *)((int)this + 0x20) *
                                     fVar15 * _DAT_005dbc4c);
            }
            iStack_a0 = iStack_a0 * 200;
            if (10000 < iStack_a0) {
              iStack_a0 = 10000;
            }
            iVar10 = (iStack_a0 + -10000) / 2;
            if (iVar10 < -10000) {
              iVar10 = -10000;
            }
            if (sound_event[5] == 1) {
              iStack_a0 = (int)(longlong)
                               ROUND((float)iVar11 * *(float *)((int)this + 0x24) *
                                     *(float *)((int)this + 0x20) * fVar15);
            }
            else {
              iStack_a0 = (int)(longlong)
                               ROUND((float)iVar11 * *(float *)((int)this + 0x28) *
                                     *(float *)((int)this + 0x20) * fVar15);
            }
            iStack_a0 = iStack_a0 * 200;
            if (10000 < iStack_a0) {
              iStack_a0 = 10000;
            }
            iVar11 = (iStack_a0 + -10000) / 2;
            if (iVar11 < -10000) {
              iVar11 = -10000;
            }
            sound_event[0x19] = iVar10;
            sound_event[0x1a] = iVar11;
          }
        }
      }
    }
    else {
LAB_004e2212:
      CGenericActiveReader__SetReader(sound_event,(void *)0x0);
    }
    if (((char)sound_event[2] != '\0') && (-1 < sound_event[1])) {
      CSoundManager__UpdateChannelParams(&DAT_00896988,sound_event,0);
    }
    if ((char)sound_event[6] == '\0') {
      dVar16 = CSoundManager__GetSampleDurationSeconds((void *)sound_event[3]);
      if (sound_event[0x1b] != -0x40800000) {
        dVar16 = (double)(float)sound_event[0x1b];
      }
      if ((((sound_event[1] < 0) || (sound_event[0x1b] != -0x40800000)) &&
          ((char)sound_event[6] == '\0')) && (dVar16 < (double)(float)sound_event[0xb])) {
        if ((sound_event[0x1f] == 1) && ((int *)*sound_event != (int *)0x0)) {
          (**(code **)(*(int *)*sound_event + 0x18))(sound_event);
        }
        if (-1 < sound_event[1]) {
          CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event);
        }
        *(undefined1 *)(sound_event + 2) = 0;
        CGenericActiveReader__SetReader(sound_event,(void *)0x0);
      }
    }
    else {
      dVar16 = CSoundManager__GetSampleDurationSeconds((void *)sound_event[3]);
      if (dVar16 < (double)(float)sound_event[0xb]) {
        do {
          dVar16 = CSoundManager__GetSampleDurationSeconds((void *)sound_event[3]);
          sound_event[0xb] = (int)((float)sound_event[0xb] - (float)dVar16);
          dVar16 = CSoundManager__GetSampleDurationSeconds((void *)sound_event[3]);
        } while (dVar16 < (double)(float)sound_event[0xb]);
      }
    }
    piVar7 = (int *)sound_event[0x1d];
    if (((char)sound_event[2] == '\0') && (*(int *)((int)this + 0x1c) == 0)) {
      if (piVar7 != (int *)0x0) {
        piVar7[0x1e] = sound_event[0x1e];
      }
      if (sound_event[0x1e] == 0) {
        *(int *)((int)this + 0xc) = sound_event[0x1d];
      }
      else {
        *(int *)(sound_event[0x1e] + 0x74) = sound_event[0x1d];
      }
      *(int *)((int)this + 8) = *(int *)((int)this + 8) + -1;
      sound_event[0x1d] = *(int *)((int)this + 0x34);
      sound_event[0x1e] = 0;
      if (*(int *)((int)this + 0x34) != 0) {
        *(int **)(*(int *)((int)this + 0x34) + 0x78) = sound_event;
      }
      *(int **)((int)this + 0x34) = sound_event;
    }
  } while( true );
}
