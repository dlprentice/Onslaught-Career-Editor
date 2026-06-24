/* address: 0x0055feec */
/* name: CDXTexture__Unk_0055feec */
/* signature: int __cdecl CDXTexture__Unk_0055feec(void * param_1) */


int __cdecl CDXTexture__Unk_0055feec(void *param_1)

{
  uint uVar1;
  uint uVar2;
  byte bVar3;
  undefined4 *puVar4;
  char *pcVar5;
  int iVar6;
  char *pcVar7;
  void *pvVar8;
  char *pcVar9;
  int iVar10;
  int local_c;
  int local_8;

  pvVar8 = param_1;
  uVar1 = *(uint *)((int)param_1 + 0x10);
  if (*(int *)((int)param_1 + 4) < 0) {
    *(undefined4 *)((int)param_1 + 4) = 0;
  }
  local_8 = CDXTexture__Unk_00568b76(uVar1,0,1);
  if (local_8 < 0) {
LAB_0055ff7a:
    local_c = -1;
  }
  else {
    uVar2 = *(uint *)((int)param_1 + 0xc);
    if ((uVar2 & 0x108) == 0) {
      return local_8 - *(int *)((int)param_1 + 4);
    }
    pcVar5 = *(char **)param_1;
    pcVar7 = *(char **)((int)param_1 + 8);
    local_c = (int)pcVar5 - (int)pcVar7;
    if ((uVar2 & 3) == 0) {
      if ((uVar2 & 0x80) == 0) {
        puVar4 = (undefined4 *)CTexture__Helper_00567aa8();
        *puVar4 = 0x16;
        goto LAB_0055ff7a;
      }
    }
    else {
      pcVar9 = pcVar7;
      if ((*(byte *)((&DAT_009d32a0)[(int)uVar1 >> 5] + 4 + (uVar1 & 0x1f) * 0x24) & 0x80) != 0) {
        for (; pcVar9 < pcVar5; pcVar9 = pcVar9 + 1) {
          if (*pcVar9 == '\n') {
            local_c = local_c + 1;
          }
        }
      }
    }
    if (local_8 != 0) {
      if ((*(byte *)((int)param_1 + 0xc) & 1) != 0) {
        if (*(int *)((int)param_1 + 4) == 0) {
          local_c = 0;
        }
        else {
          pcVar5 = pcVar5 + (*(int *)((int)param_1 + 4) - (int)pcVar7);
          iVar10 = (uVar1 & 0x1f) * 0x24;
          if ((*(byte *)(iVar10 + 4 + (&DAT_009d32a0)[(int)uVar1 >> 5]) & 0x80) != 0) {
            iVar6 = CDXTexture__Unk_00568b76(uVar1,0,2);
            if (iVar6 == local_8) {
              pcVar7 = *(char **)((int)param_1 + 8);
              pcVar9 = pcVar5 + (int)pcVar7;
              param_1 = pcVar5;
              for (; pcVar7 < pcVar9; pcVar7 = pcVar7 + 1) {
                if (*pcVar7 == '\n') {
                  param_1 = (void *)((int)param_1 + 1);
                }
              }
              bVar3 = *(byte *)((int)pvVar8 + 0xd) & 0x20;
            }
            else {
              CDXTexture__Unk_00568b76(uVar1,local_8,0);
              pvVar8 = (void *)0x200;
              if ((((char *)0x200 < pcVar5) || ((*(uint *)((int)param_1 + 0xc) & 8) == 0)) ||
                 ((*(uint *)((int)param_1 + 0xc) & 0x400) != 0)) {
                pvVar8 = *(void **)((int)param_1 + 0x18);
              }
              bVar3 = *(byte *)(iVar10 + 4 + (&DAT_009d32a0)[(int)uVar1 >> 5]) & 4;
              param_1 = pvVar8;
            }
            pcVar5 = param_1;
            if (bVar3 != 0) {
              pcVar5 = (void *)((int)param_1 + 1);
            }
          }
          param_1 = pcVar5;
          local_8 = local_8 - (int)param_1;
        }
      }
      local_c = local_c + local_8;
    }
  }
  return local_c;
}
