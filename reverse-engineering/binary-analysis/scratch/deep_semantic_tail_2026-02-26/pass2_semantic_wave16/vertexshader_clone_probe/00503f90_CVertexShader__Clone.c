/* address: 0x00503f90 */
/* name: CVertexShader__Clone */
/* signature: undefined CVertexShader__Clone(void) */


int * CVertexShader__Clone(void *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  void *file;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int unaff_EDI;
  char local_d4 [200];
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d575c;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  iVar2 = OID__AllocObject(0x5c,0x50,s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,0x99a);
  piVar6 = (int *)0x0;
  local_4 = 0;
  if (iVar2 != 0) {
    piVar6 = (int *)CVertexShader__CVertexShader();
  }
  iVar2 = *piVar6;
  iVar5 = piVar6[1];
  iVar1 = piVar6[0x16];
  local_4 = 0xffffffff;
  CMeshPart__Helper_00423910((uint)param_1);
  CMeshPart__Helper_00423910((uint)param_1);
  CMeshPart__Helper_00423960(param_1,(int)piVar6,0x5c,1,unaff_EDI);
  piVar6[1] = iVar5;
  piVar6[0x16] = iVar1;
  *piVar6 = iVar2;
  if (piVar6[0xe] != 0) {
    iVar2 = OID__AllocObject(piVar6[0xf] & 0xfffffffc,0x50,
                             s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,0x9c6);
    piVar6[0xe] = iVar2;
    CMeshPart__Helper_00423910((uint)param_1);
    CMeshPart__Helper_00423960(param_1,piVar6[0xe],piVar6[0xf],1,unaff_EDI);
  }
  if (piVar6[0x11] != 0) {
    iVar2 = OID__AllocObject(DAT_00854e74 * 4,0x50,s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,0x9d2
                            );
    piVar6[0x11] = iVar2;
    CMeshPart__Helper_00423910((uint)param_1);
    CMeshPart__Helper_00423960(param_1,piVar6[0x11],4,DAT_00854e74,unaff_EDI);
  }
  if (piVar6[0x10] != 0) {
    CMeshPart__Helper_00423910((uint)param_1);
    iVar2 = OID__AllocObject(DAT_00854e74 * 4,0x50,s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,0x9e3
                            );
    piVar6[0x10] = iVar2;
    iVar2 = 0;
    if (0 < DAT_00854e74) {
      piVar4 = (int *)piVar6[0x11];
      iVar5 = DAT_00854e74;
      do {
        iVar1 = *piVar4;
        piVar4 = piVar4 + 1;
        iVar2 = iVar2 + iVar1;
        iVar5 = iVar5 + -1;
      } while (iVar5 != 0);
    }
    uVar3 = OID__AllocObject(iVar2 * 4,0x50,s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,0x9ef);
    iVar5 = 0;
    *(undefined4 *)piVar6[0x10] = uVar3;
    iVar2 = *(int *)piVar6[0x10];
    if (0 < DAT_00854e74) {
      do {
        *(int *)(piVar6[0x10] + iVar5 * 4) = iVar2;
        CMeshPart__Helper_00423960
                  (param_1,*(int *)(piVar6[0x10] + iVar5 * 4),4,*(int *)(piVar6[0x11] + iVar5 * 4),
                   unaff_EDI);
        iVar5 = iVar5 + 1;
        iVar2 = iVar2 + *(int *)(piVar6[0x11] + -4 + iVar5 * 4) * 4;
      } while (iVar5 < DAT_00854e74);
    }
  }
  if ((void *)piVar6[0x11] != (void *)0x0) {
    OID__FreeObject((void *)piVar6[0x11]);
    piVar6[0x11] = 0;
  }
  if (piVar6[0x14] != 0) {
    CMeshPart__Helper_00423910((uint)param_1);
    iVar2 = OID__AllocObject(piVar6[0x15],0x50,s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,0xa0b);
    piVar6[0x14] = iVar2;
    CMeshPart__Helper_00423960(param_1,iVar2,piVar6[0x15],1,unaff_EDI);
  }
  if (piVar6[0x12] != 0) {
    CMeshPart__Helper_00423910((uint)param_1);
    if (DAT_00662f35 == '\0') {
      iVar2 = OID__AllocObject(piVar6[0x13] + 1,0x50,s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,
                               0xa3d);
      piVar6[0x12] = iVar2;
      CMeshPart__Helper_00423960(param_1,iVar2,piVar6[0x13],1,unaff_EDI);
      *(undefined1 *)(piVar6[0x13] + piVar6[0x12]) = 0;
    }
    else {
      iVar2 = piVar6[0x13] * 2 + 10000;
      iVar5 = OID__AllocObject(iVar2,0x50,s_C__dev_ONSLAUGHT2_VertexShader_c_0063cf78,0xa1e);
      piVar6[0x12] = iVar5;
      CMeshPart__Helper_00423960(param_1,iVar5,piVar6[0x13],1,unaff_EDI);
      sprintf(local_d4,s_shader_03d_i_0063d100);
      file = fopen(local_d4,&DAT_00629038);
      if (file != (void *)0x0) {
        iVar5 = fread((void *)piVar6[0x12],1,iVar2,file);
        if (iVar5 == iVar2) {
          FatalError_LocalizedStringId('\0',0xd2,0xc9);
        }
        *(undefined1 *)(piVar6[0x12] + iVar5) = 0;
        piVar6[0x13] = iVar5;
        fclose(file);
      }
    }
  }
  CVertexShader__CompileShader();
  OID__FreeObject((void *)piVar6[0x12]);
  piVar6[0x12] = 0;
  piVar6[0x13] = 0;
  (**(code **)(*piVar6 + 8))();
  ExceptionList = pvStack_c;
  return piVar6;
}
