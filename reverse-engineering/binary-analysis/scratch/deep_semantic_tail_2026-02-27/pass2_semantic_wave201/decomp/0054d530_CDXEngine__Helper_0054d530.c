/* address: 0x0054d530 */
/* name: CDXEngine__Helper_0054d530 */
/* signature: void __thiscall CDXEngine__Helper_0054d530(void * this, int param_1, void * param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDXEngine__Helper_0054d530(void *this,int param_1,void *param_2,uint param_3)

{
  int iVar1;
  char cVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int extraout_EAX;
  void *pvVar7;
  uint uVar8;
  int *piVar9;
  int iVar10;
  int unaff_EBP;
  int iVar11;
  int iVar12;
  float10 fVar13;
  double dVar14;
  int iStack_a4;
  int local_a0;
  int iStack_90;
  uint uStack_88;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  float fStack_50;
  float fStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  float fStack_10;
  float fStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;

  if (0 < *(int *)((int)this + 0x108)) {
    local_a0 = 0;
    if ((param_1 != 0) && (iVar5 = (**(code **)(*(int *)param_1 + 0x1c))(), -1 < iVar5)) {
      fVar13 = (float10)(**(code **)(*(int *)param_1 + 0x18))();
      iVar12 = *(int *)(*(int *)(*(int *)((int)this + 0x10c) + 0x128) + 0x18);
      dVar14 = CDXEngine__Helper_0055dfe7
                         ((double)(fVar13 * (float10)*(int *)(iVar12 + 0x1c + iVar5 * 0x24) +
                                  (float10)*(int *)(iVar12 + iVar5 * 0x24 + 0x14)));
      iStack_90 = (int)(longlong)ROUND(dVar14);
      local_a0 = iStack_90 % *(int *)(*(int *)((int)this + 0x10c) + 0xb8);
    }
    if ((*(int *)((int)this + 0x110) != 0) || (DAT_0089ce90 != (void *)0x0)) {
      if (DAT_00854e6c != '\0') {
        CEngine__SetVertexShadersEnabled(&DAT_00855bb0,'\x01');
      }
      pvVar7 = *(void **)((int)this + 0x110);
      if ((*(void **)((int)this + 0x110) != (void *)0x0) ||
         (pvVar7 = DAT_0089ce90, DAT_0089ce90 != (void *)0x0)) {
        CVertexShader__ApplyRenderStateShaderConstants((int)pvVar7);
      }
    }
    if (*(void **)((int)this + 0x110) == (void *)0x0) {
      if (DAT_0089ce90 == (void *)0x0) {
        _DAT_009c73d4 = *(undefined4 *)((int)this + 0x118);
        DAT_009c741c = 1;
      }
      else {
        CEngine__SetShaderObject(&DAT_00855bb0,DAT_0089ce90);
      }
    }
    else {
      CEngine__SetShaderObject(&DAT_00855bb0,*(void **)((int)this + 0x110));
    }
    if ((*(int *)((int)this + 0x110) == 0) && (DAT_0089ce90 == (void *)0x0)) {
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\x01');
    }
    uVar3 = DAT_0063012c;
    iVar12 = 0;
    iVar5 = *(int *)((int)this + 0x108);
    if (0 < iVar5) {
      uVar8 = (uint)param_2 & 0x10;
      do {
        iVar10 = 6;
        iStack_a4 = 6;
        if (uVar8 == 0x10) {
          iVar10 = 1;
          iStack_a4 = 1;
        }
        if ((DAT_00704e48 == 8) || (DAT_00704e48 == 4)) {
          iVar10 = 1;
          iStack_a4 = 1;
        }
        if (DAT_00630130 == 0) {
          iVar10 = 1;
          iStack_a4 = 1;
        }
        if (((uint)param_2 & 0x40) != 0) {
          iVar10 = 0;
          iStack_a4 = 0;
        }
        iVar11 = *(int *)((int)this + iVar12 * 4 + 8);
        if (*(int *)(iVar11 + 0x1c) == 0) {
          iVar10 = 0;
          iStack_a4 = 0;
        }
        (**(code **)(*DAT_00888a50 + 0x1a0))(DAT_00888a50,*(undefined4 *)(iVar11 + 4));
        (**(code **)(*DAT_00888a50 + 400))
                  (DAT_00888a50,0,**(undefined4 **)((int)this + iVar12 * 4 + 8),0,
                   *(undefined4 *)((int)this + 0x114));
        iVar11 = 0;
        if (iVar10 != 0) {
          do {
            if ((&DAT_009c63a4)[iVar11] != '\x02') {
              iVar10 = *(int *)((int)this + iVar12 * 4 + 8);
              iVar6 = *(int *)(iVar10 + 0x20 + iVar11 * 4);
              if (iVar6 != 0) {
                if (DAT_00704e48 == 8) {
                  switch(*(undefined4 *)((int)this + 0x11c)) {
                  default:
                    iVar6 = 1;
                    break;
                  case 1:
                    iVar6 = 2;
                    break;
                  case 2:
                    iVar6 = 3;
                    break;
                  case 3:
                    iVar6 = 4;
                    break;
                  case 4:
                    iVar6 = 5;
                    break;
                  case 5:
                    iVar6 = 6;
                  }
                  CEngine__DrawIndexedPrimitives
                            (&DAT_00855bb0,iVar6,0,*(int *)(iVar10 + 0x14),0,*(int *)(iVar10 + 0x18)
                            );
                }
                else {
                  uStack_88 = (uint)(longlong)
                                    ROUND((float)(int)uVar3 *
                                          *(float *)(*(int *)(iVar6 + 0xc) +
                                                    (local_a0 % *(int *)(iVar6 + 8)) * 4));
                  if (iVar11 != 0) {
                    uStack_88 = (DAT_00630130 * uStack_88) / 100;
                  }
                  if (10 < (int)uStack_88) {
                    DAT_0063012c = uStack_88;
                    if (uVar8 == 0x10) {
                      DAT_006601ac[0x22] = 5;
                      iVar10 = CVBufTexture__RenderModePass(DAT_006601ac);
                      cVar2 = (char)iVar10;
                      (**(code **)(*DAT_006601ac + 0x20))();
                      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\x01');
                    }
                    else {
                      *(int *)(**(int **)(*(int *)((int)this + iVar12 * 4 + 8) + 0x20 + iVar11 * 4)
                              + 0x88) = iVar11;
                      piVar9 = *(int **)(*(int *)((int)this + iVar12 * 4 + 8) + 0x20 + iVar11 * 4);
                      *(undefined4 *)(*piVar9 + 0x8c) =
                           *(undefined4 *)(piVar9[4] + (local_a0 % piVar9[2]) * 4);
                      piVar9 = *(int **)(*(int *)((int)this + iVar12 * 4 + 8) + 0x20 + iVar11 * 4);
                      *(undefined4 *)(*piVar9 + 0x90) =
                           *(undefined4 *)(piVar9[5] + (local_a0 % piVar9[2]) * 4);
                      piVar9 = *(int **)(*(int *)((int)this + iVar12 * 4 + 8) + 0x20 + iVar11 * 4);
                      *(undefined4 *)(*piVar9 + 0x94) =
                           *(undefined4 *)(piVar9[6] + (local_a0 % piVar9[2]) * 4);
                      piVar9 = *(int **)(*(int *)((int)this + iVar12 * 4 + 8) + 0x20 + iVar11 * 4);
                      *(undefined4 *)(*piVar9 + 0x98) =
                           *(undefined4 *)(piVar9[7] + (local_a0 % piVar9[2]) * 4);
                      iVar10 = CVBufTexture__RenderModePass
                                         ((void *)**(undefined4 **)
                                                    (*(int *)((int)this + iVar12 * 4 + 8) + 0x20 +
                                                    iVar11 * 4));
                      cVar2 = (char)iVar10;
                      (**(code **)(*(int *)**(undefined4 **)
                                             (*(int *)((int)this + iVar12 * 4 + 8) + 0x20 +
                                             iVar11 * 4) + 0x20))();
                    }
                    if (cVar2 != '\0') {
                      if (((iVar11 == 0) || ((&DAT_009c63a4)[iVar11] != '\0')) ||
                         (CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0), -1 < extraout_EAX)) {
                        (&DAT_009c63a4)[iVar11] = 1;
                        iVar10 = *(int *)((int)this + iVar12 * 4 + 8);
                        if (((*(int *)(**(int **)(iVar10 + 0x20 + iVar11 * 4) + 0xb4) == 0) ||
                            (iVar11 != 0)) || (DAT_00704e48 == 4)) {
                          switch(*(undefined4 *)((int)this + 0x11c)) {
                          default:
                            iVar6 = 1;
                            break;
                          case 1:
                            iVar6 = 2;
                            break;
                          case 2:
                            iVar6 = 3;
                            break;
                          case 3:
                            iVar6 = 4;
                            break;
                          case 4:
                            iVar6 = 5;
                            break;
                          case 5:
                            iVar6 = 6;
                          }
                          CEngine__DrawIndexedPrimitives
                                    (&DAT_00855bb0,iVar6,0,*(int *)(iVar10 + 0x14),0,
                                     *(int *)(iVar10 + 0x18));
                        }
                        else {
                          iVar10 = CWaterRenderSystem__Helper_00527cc0(&DAT_009c6390,1,unaff_EBP);
                          if ((char)iVar10 == '\0') {
                            RenderState_Set(0x1b,0);
                            RenderState_Set(0xf,0);
                            CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
                            switch(*(undefined4 *)((int)this + 0x11c)) {
                            default:
                              iVar10 = 1;
                              break;
                            case 1:
                              iVar10 = 2;
                              break;
                            case 2:
                              iVar10 = 3;
                              break;
                            case 3:
                              iVar10 = 4;
                              break;
                            case 4:
                              iVar10 = 5;
                              break;
                            case 5:
                              iVar10 = 6;
                            }
                            iVar6 = *(int *)((int)this + iVar12 * 4 + 8);
                            CEngine__DrawIndexedPrimitives
                                      (&DAT_00855bb0,iVar10,0,*(int *)(iVar6 + 0x14),0,
                                       *(int *)(iVar6 + 0x18));
                            iVar10 = DAT_00855578;
                            RenderState_Set(0xe,0);
                            RenderState_Set(0x1b,1);
                            RenderState_Set(0xf,1);
                            cVar2 = DAT_009c68ad;
                            DAT_009c68ad = 0;
                            DAT_009c6910 = 1;
                            CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
                            switch(*(undefined4 *)((int)this + 0x11c)) {
                            default:
                              iVar6 = 1;
                              break;
                            case 1:
                              iVar6 = 2;
                              break;
                            case 2:
                              iVar6 = 3;
                              break;
                            case 3:
                              iVar6 = 4;
                              break;
                            case 4:
                              iVar6 = 5;
                              break;
                            case 5:
                              iVar6 = 6;
                            }
                            iVar1 = *(int *)((int)this + iVar12 * 4 + 8);
                            CEngine__DrawIndexedPrimitives
                                      (&DAT_00855bb0,iVar6,0,*(int *)(iVar1 + 0x14),0,
                                       *(int *)(iVar1 + 0x18));
                            RenderState_Set(0x1b,0);
                            DAT_009c68ad = cVar2 != '\0';
                            DAT_009c6910 = 1;
                            CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
                            RenderState_Set(0xe,iVar10);
                          }
                          else {
                            RenderState_Set(0x1b,0);
                            RenderState_Set(0xf,0);
                            D3DStateCache__SetStateCached(1,1,0xd);
                            D3DStateCache__SetStateCached(1,2,2);
                            D3DStateCache__SetStateCached(1,3,1);
                            D3DStateCache__SetStateCached(1,0xb,0);
                            pvVar7 = CDXTexture__GetAnimatedFrame
                                               ((void *)**(undefined4 **)
                                                          (*(int *)((int)this + iVar12 * 4 + 8) +
                                                          0x20));
                            CEngine__SetRenderStateCached(&DAT_00855bb0,1,(int)pvVar7);
                            iVar10 = CDXLandscape__Helper_00527d20(0x9c6390);
                            if ((char)iVar10 != '\0') {
                              switch(*(undefined4 *)((int)this + 0x11c)) {
                              default:
                                iVar10 = 1;
                                break;
                              case 1:
                                iVar10 = 2;
                                break;
                              case 2:
                                iVar10 = 3;
                                break;
                              case 3:
                                iVar10 = 4;
                                break;
                              case 4:
                                iVar10 = 5;
                                break;
                              case 5:
                                iVar10 = 6;
                              }
                              iVar6 = *(int *)((int)this + iVar12 * 4 + 8);
                              CEngine__DrawIndexedPrimitives
                                        (&DAT_00855bb0,iVar10,0,*(int *)(iVar6 + 0x14),0,
                                         *(int *)(iVar6 + 0x18));
                              CVBufTexture__MarkAccepted(0x9c6390);
                            }
                            D3DStateCache__SetStateRaw(1,1,1);
                            RenderState_Set(0xf,1);
                          }
                        }
                      }
                      else {
                        CConsole__Printf(&DAT_0066eb90,s_Mesh_layer__d_disabled_006512d8);
                        (&DAT_009c63a4)[iVar11] = 2;
                      }
                    }
                    piVar9 = DAT_006601ac;
                    if (uVar8 != 0x10) {
                      piVar9 = (int *)**(undefined4 **)
                                        (*(int *)((int)this + iVar12 * 4 + 8) + 0x20 + iVar11 * 4);
                    }
                    CVBufTexture__SetupRenderStates(piVar9,'\x01');
                  }
                }
              }
            }
            iVar11 = iVar11 + 1;
          } while (iVar11 < iStack_a4);
        }
        if (((((uint)param_2 & 0x40) != 0) && (DAT_00704e48 != 4)) &&
           (*(int *)(*(int *)((int)this + iVar12 * 4 + 8) + 0x1c) != 0)) {
          DAT_0089c9c4[0x22] = 2;
          CVBufTexture__RenderModePass(DAT_0089c9c4);
          (**(code **)(*DAT_0089c9c4 + 0x20))();
          RenderState_Set(0x89,0);
          dVar14 = CDXMeshVB__Helper_0044a0c0();
          fStack_50 = (float)dVar14 * _DAT_005d8c1c;
          uStack_80 = 0x3f000000;
          uStack_7c = 0;
          uStack_78 = 0;
          uStack_74 = 0;
          fStack_4c = fStack_50 * _DAT_005d85ec;
          uStack_70 = 0;
          uStack_6c = 0xbf000000;
          uStack_68 = 0;
          uStack_64 = 0;
          uStack_60 = 0;
          uStack_5c = 0;
          uStack_58 = 0x3f800000;
          uStack_54 = 0;
          uStack_48 = 0;
          uStack_44 = 0x3f800000;
          (**(code **)(*DAT_00888a50 + 0xb0))(DAT_00888a50,0x10,&uStack_80);
          RenderState_Set(0x13,5);
          RenderState_Set(0x14,2);
          CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\x01');
          switch(*(undefined4 *)((int)this + 0x11c)) {
          default:
            iVar10 = 1;
            break;
          case 1:
            iVar10 = 2;
            break;
          case 2:
            iVar10 = 3;
            break;
          case 3:
            iVar10 = 4;
            break;
          case 4:
            iVar10 = 5;
            break;
          case 5:
            iVar10 = 6;
          }
          iVar11 = *(int *)((int)this + iVar12 * 4 + 8);
          CEngine__DrawIndexedPrimitives
                    (&DAT_00855bb0,iVar10,0,*(int *)(iVar11 + 0x14),0,*(int *)(iVar11 + 0x18));
          CVBufTexture__SetupRenderStates(DAT_0089c9c4,'\x01');
          DAT_0089c9c4[0x22] = 0;
          RenderState_Set(0x89,1);
          RenderState_Set(0x13,5);
          RenderState_Set(0x14,6);
        }
        if ((((((uint)param_2 & 0x20) != 0) && (DAT_00704e48 != 4)) &&
            (*(int *)(*(int *)((int)this + iVar12 * 4 + 8) + 0x1c) != 0)) &&
           (iVar10 = CWaterRenderSystem__Helper_00527cc0(&DAT_009c63b0,1,unaff_EBP),
           uVar4 = DAT_0063012c, (char)iVar10 != '\0')) {
          DAT_0063012c = (int)(DAT_0063012c * DAT_00704e64) / 100;
          DAT_0089c9c0[0x22] = 2;
          CVBufTexture__RenderModePass(DAT_0089c9c0);
          (**(code **)(*DAT_0089c9c0 + 0x20))();
          RenderState_Set(0x89,0);
          dVar14 = CDXMeshVB__Helper_0044a0c0();
          fStack_10 = (float)dVar14 * _DAT_005d8c68;
          uStack_40 = 0x3f000000;
          uStack_3c = 0;
          uStack_38 = 0;
          uStack_34 = 0;
          fStack_c = fStack_10 * _DAT_005d85ec;
          uStack_30 = 0;
          uStack_2c = 0xbf000000;
          uStack_28 = 0;
          uStack_24 = 0;
          uStack_20 = 0;
          uStack_1c = 0;
          uStack_18 = 0x3f800000;
          uStack_14 = 0;
          uStack_8 = 0;
          uStack_4 = 0x3f800000;
          (**(code **)(*DAT_00888a50 + 0xb0))(DAT_00888a50,0x10,&uStack_40);
          RenderState_Set(0x13,5);
          RenderState_Set(0x14,2);
          CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\x01');
          iVar10 = CDXLandscape__Helper_00527d20(0x9c63b0);
          if ((char)iVar10 != '\0') {
            CVBufTexture__MarkAccepted(0x9c63b0);
            switch(*(undefined4 *)((int)this + 0x11c)) {
            default:
              iVar10 = 1;
              break;
            case 1:
              iVar10 = 2;
              break;
            case 2:
              iVar10 = 3;
              break;
            case 3:
              iVar10 = 4;
              break;
            case 4:
              iVar10 = 5;
              break;
            case 5:
              iVar10 = 6;
            }
            iVar11 = *(int *)((int)this + iVar12 * 4 + 8);
            CEngine__DrawIndexedPrimitives
                      (&DAT_00855bb0,iVar10,0,*(int *)(iVar11 + 0x14),0,*(int *)(iVar11 + 0x18));
          }
          CVBufTexture__SetupRenderStates(DAT_0089c9c0,'\x01');
          DAT_0089c9c0[0x22] = 0;
          DAT_0063012c = uVar4;
          RenderState_Set(0x89,1);
          RenderState_Set(0x13,5);
          RenderState_Set(0x14,6);
        }
        iVar12 = iVar12 + 1;
      } while (iVar12 < iVar5);
    }
    DAT_0063012c = uVar3;
    if ((*(int *)((int)this + 0x110) != 0) && (DAT_00854e6c != '\0')) {
      CEngine__SetVertexShadersEnabled(&DAT_00855bb0,'\0');
    }
    D3DStateCache__SetStateCached(1,0xb,1);
  }
  return;
}
