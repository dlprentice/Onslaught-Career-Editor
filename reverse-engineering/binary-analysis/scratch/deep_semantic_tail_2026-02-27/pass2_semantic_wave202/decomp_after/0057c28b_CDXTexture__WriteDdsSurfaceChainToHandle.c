/* address: 0x0057c28b */
/* name: CDXTexture__WriteDdsSurfaceChainToHandle */
/* signature: int __thiscall CDXTexture__WriteDdsSurfaceChainToHandle(void * this, void * param_1, int param_2) */


int __thiscall CDXTexture__WriteDdsSurfaceChainToHandle(void *this,void *param_1,int param_2)

{
  void *pvVar1;
  int iVar2;
  LPCVOID lpBuffer;
  uint uVar3;
  DWORD nNumberOfBytesToWrite;
  int *piVar4;
  int *piVar5;
  uint *puVar6;
  int *piVar7;
  uint uVar8;
  uint local_98 [5];
  uint local_84;
  int local_80;
  int local_50 [8];
  uint local_30;
  byte local_2b;
  byte local_2a;
  undefined4 local_1c;
  int *local_18;
  uint local_14;
  DWORD local_10;
  int *local_c;
  uint local_8;

  local_8 = 0;
  for (pvVar1 = this; pvVar1 != (void *)0x0; pvVar1 = *(void **)((int)pvVar1 + 0x4c)) {
    local_8 = local_8 + 1;
  }
  piVar4 = &DAT_00657290;
  if (DAT_00657290 != 0) {
    iVar2 = DAT_00657290;
    do {
      if (iVar2 == *(int *)this) break;
      piVar4 = piVar4 + 9;
      iVar2 = *piVar4;
    } while (iVar2 != 0);
  }
  if (*piVar4 == 0) {
    iVar2 = -0x7fffbffb;
  }
  else {
    local_18 = this;
    local_c = CDXTexture__FindFormatDescriptorById(*(int *)this);
    local_14 = (uint)local_c[2] >> 3;
    local_1c = 0x20534444;
    WriteFile(param_1,&local_1c,4,&local_10,(LPOVERLAPPED)0x0);
    puVar6 = local_98;
    for (iVar2 = 0x1f; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar6 = 0;
      puVar6 = puVar6 + 1;
    }
    local_98[2] = *(undefined4 *)((int)this + 0x10);
    local_98[3] = *(undefined4 *)((int)this + 0xc);
    uVar3 = piVar4[2];
    local_98[0] = 0x7c;
    local_98[1] = 0x1007;
    piVar7 = local_50;
    for (iVar2 = 8; piVar5 = local_18, piVar4 = piVar4 + 1, iVar2 != 0; iVar2 = iVar2 + -1) {
      *piVar7 = *piVar4;
      piVar7 = piVar7 + 1;
    }
    local_30 = 0x1000;
    if ((uVar3 & 3) != 0) {
      local_30 = 0x1002;
    }
    if ((uVar3 & 0x20) != 0) {
      local_30 = local_30 | 0x100;
    }
    if (local_18[0x13] != 0) {
      local_30 = local_30 | 0x400008;
      local_98[1] = 0x21007;
      local_80 = local_8;
    }
    if (local_18[0x14] != 0) {
      local_30 = local_30 | 8;
      local_2b = local_2b | 0xfe;
    }
    if (1 < (uint)local_18[5]) {
      local_98[1] = local_98[1] | 0x800000;
      local_2a = local_2a | 0x20;
      local_84 = local_18[5];
    }
    WriteFile(param_1,local_98,0x7c,&local_10,(LPOVERLAPPED)0x0);
    if (local_c[1] == 1) {
      WriteFile(param_1,(LPCVOID)piVar5[2],0x400,&local_10,(LPOVERLAPPED)0x0);
    }
    local_c = piVar5;
    do {
      for (; piVar5 != (int *)0x0; piVar5 = (int *)piVar5[0x13]) {
        local_8 = 0;
        if (piVar5[5] != 0) {
          uVar3 = piVar5[4];
          do {
            uVar8 = 0;
            if (uVar3 != 0) {
              do {
                iVar2 = *local_18;
                if (iVar2 < 0x34545845) {
                  if (iVar2 == 0x34545844) {
LAB_0057c425:
                    iVar2 = (piVar5[7] + uVar8 >> 2) * piVar5[0xc] +
                            (piVar5[10] + local_8) * piVar5[0xd] + ((uint)piVar5[6] >> 2) * 0x10;
                    nNumberOfBytesToWrite = (piVar5[3] + 3U >> 2) << 4;
                  }
                  else {
                    if (iVar2 != 0x31545844) {
                      if (iVar2 != 0x32545844) {
                        if (iVar2 == 0x32595559) goto LAB_0057c52b;
                        if (iVar2 != 0x33545844) goto LAB_0057c4fe;
                      }
                      goto LAB_0057c425;
                    }
                    iVar2 = (piVar5[7] + uVar8 >> 2) * piVar5[0xc] +
                            (piVar5[10] + local_8) * piVar5[0xd] + ((uint)piVar5[6] >> 2) * 8;
                    nNumberOfBytesToWrite = (piVar5[3] + 3U >> 2) << 3;
                  }
                  lpBuffer = (LPCVOID)(iVar2 + piVar5[1]);
                  uVar8 = uVar8 + 3;
                }
                else {
                  if (iVar2 == 0x35545844) goto LAB_0057c425;
                  if (((iVar2 == 0x42475247) || (iVar2 == 0x47424752)) || (iVar2 == 0x59565955)) {
LAB_0057c52b:
                    lpBuffer = (LPCVOID)((piVar5[10] + local_8) * piVar5[0xd] +
                                         (piVar5[7] + uVar8) * piVar5[0xc] + piVar5[6] * local_14 +
                                        piVar5[1]);
                    nNumberOfBytesToWrite = (piVar5[3] + 1U >> 1) << 2;
                  }
                  else {
LAB_0057c4fe:
                    lpBuffer = (LPCVOID)((piVar5[10] + local_8) * piVar5[0xd] +
                                         (piVar5[7] + uVar8) * piVar5[0xc] + piVar5[6] * local_14 +
                                        piVar5[1]);
                    nNumberOfBytesToWrite = piVar5[3] * local_14;
                  }
                }
                WriteFile(param_1,lpBuffer,nNumberOfBytesToWrite,&local_10,(LPOVERLAPPED)0x0);
                uVar3 = piVar5[4];
                uVar8 = uVar8 + 1;
              } while (uVar8 < uVar3);
            }
            local_8 = local_8 + 1;
          } while (local_8 < (uint)piVar5[5]);
        }
      }
      piVar5 = (int *)local_c[0x14];
      local_c = piVar5;
    } while (piVar5 != (int *)0x0);
    iVar2 = 0;
  }
  return iVar2;
}
