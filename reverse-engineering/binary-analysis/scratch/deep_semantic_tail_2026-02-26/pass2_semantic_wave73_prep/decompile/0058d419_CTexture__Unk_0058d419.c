/* address: 0x0058d419 */
/* name: CTexture__Unk_0058d419 */
/* signature: int __thiscall CTexture__Unk_0058d419(void * this, void * param_1, void * param_2, void * param_3, void * param_4) */


int __thiscall
CTexture__Unk_0058d419(void *this,void *param_1,void *param_2,void *param_3,void *param_4)

{
  char *pcVar1;
  byte extraout_AL;
  char cVar2;
  undefined1 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int unaff_ESI;
  char *pcVar8;
  int unaff_EDI;
  char local_20 [27];
  byte local_5;

  cVar2 = *(char *)param_1;
  pcVar8 = param_1;
  while (cVar2 != '\0') {
    pcVar1 = (char *)(int)*pcVar8;
    uVar4 = CTexture__Helper_0056a05b(this,(char *)(int)*pcVar8,unaff_ESI);
    this = pcVar1;
    if (uVar4 == 0) break;
    pcVar8 = pcVar8 + 1;
    cVar2 = *pcVar8;
  }
  if (*pcVar8 == '\0') {
    local_5 = 0;
  }
  else {
    this = pcVar8;
    CSoundManager__Helper_0055e2a6(pcVar8);
    local_5 = extraout_AL;
  }
  if (0xf < local_5) {
    *(undefined1 *)param_2 = 0;
    *(undefined1 *)param_3 = 0xff;
    return -0x7fffbffb;
  }
  uVar4 = (int)pcVar8 - (int)param_1;
  if ((uVar4 == 0) || (0x14 < uVar4)) {
    return -0x7fffbffb;
  }
  cVar2 = *pcVar8;
  if (cVar2 != '\0') {
    do {
      pcVar1 = (char *)(int)cVar2;
      uVar5 = CTexture__Helper_0056a089(this,(char *)(int)cVar2,unaff_EDI);
      this = pcVar1;
      if (uVar5 == 0) break;
      pcVar8 = pcVar8 + 1;
      cVar2 = *pcVar8;
    } while (cVar2 != '\0');
    if (*pcVar8 != '\0') {
      return -0x7fffbffb;
    }
  }
  if (*(char *)param_1 != '\0') {
    iVar7 = -(int)param_1;
    do {
      uVar5 = CTexture__Helper_0056a05b(this,(void *)(int)*(char *)param_1,unaff_EDI);
      if (uVar5 == 0) break;
      this = (void *)(int)*(char *)param_1;
      iVar6 = CTexture__Helper_0055e673((int)this);
      *(char *)((int)param_1 + (int)(local_20 + iVar7)) = (char)iVar6;
      param_1 = (void *)((int)param_1 + 1);
    } while (*(char *)param_1 != '\0');
  }
  iVar7 = _strncmp(local_20,"POSITION",uVar4);
  if (iVar7 == 0) {
    uVar3 = 0;
  }
  else {
    iVar7 = _strncmp(local_20,"BLENDWEIGHT",uVar4);
    if (iVar7 == 0) {
      uVar3 = 1;
    }
    else {
      iVar7 = _strncmp(local_20,"BLENDINDICES",uVar4);
      if (iVar7 == 0) {
        uVar3 = 2;
      }
      else {
        iVar7 = _strncmp(local_20,"NORMAL",uVar4);
        if (iVar7 == 0) {
          uVar3 = 3;
        }
        else {
          iVar7 = _strncmp(local_20,"PSIZE",uVar4);
          if (iVar7 == 0) {
            uVar3 = 4;
          }
          else {
            iVar7 = _strncmp(local_20,"TEXCOORD",uVar4);
            if (iVar7 == 0) {
              uVar3 = 5;
            }
            else {
              iVar7 = _strncmp(local_20,"TANGENT",uVar4);
              if (iVar7 == 0) {
                uVar3 = 6;
              }
              else {
                iVar7 = _strncmp(local_20,"BINORMAL",uVar4);
                if (iVar7 == 0) {
                  uVar3 = 7;
                }
                else {
                  iVar7 = _strncmp(local_20,"TESSFACTOR",uVar4);
                  if (iVar7 == 0) {
                    uVar3 = 8;
                  }
                  else {
                    iVar7 = _strncmp(local_20,"POSITIONT ",uVar4);
                    if (iVar7 == 0) {
                      uVar3 = 9;
                    }
                    else {
                      iVar7 = _strncmp(local_20,"COLOR",uVar4);
                      if (iVar7 != 0) {
                        iVar7 = _strncmp(local_20,"FOG",uVar4);
                        if (iVar7 == 0) {
                          uVar3 = 0xb;
                          goto LAB_0058d697;
                        }
                        iVar7 = _strncmp(local_20,"DEPTH",uVar4);
                        if (iVar7 == 0) {
                          uVar3 = 0xc;
                          goto LAB_0058d697;
                        }
                        iVar7 = _strncmp(local_20,"SAMPLE",uVar4);
                        if (iVar7 == 0) {
                          uVar3 = 0xd;
                          goto LAB_0058d697;
                        }
                        iVar7 = _strncmp(local_20,"DIFFUSE",uVar4);
                        if (iVar7 == 0) {
                          local_5 = 0;
                        }
                        else {
                          iVar7 = _strncmp(local_20,"SPECULAR",uVar4);
                          if (iVar7 != 0) {
                            return -0x7fffbffb;
                          }
                          local_5 = 1;
                        }
                      }
                      uVar3 = 10;
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
LAB_0058d697:
  *(undefined1 *)param_2 = uVar3;
  *(byte *)param_3 = local_5;
  return 0;
}
