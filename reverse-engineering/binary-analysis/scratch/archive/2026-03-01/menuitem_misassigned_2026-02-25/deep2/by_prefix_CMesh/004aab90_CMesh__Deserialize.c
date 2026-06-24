/* address: 0x004aab90 */
/* name: CMesh__Deserialize */
/* signature: undefined CMesh__Deserialize(void) */


int * CMesh__Deserialize(void *param_1,void *param_2)

{
  bool bVar1;
  undefined3 extraout_var;
  int iVar2;
  int iVar3;
  int *piVar4;
  void *pvVar5;
  int *piVar6;
  void *unaff_EDI;
  char local_351;
  int local_350;
  int *local_34c;
  int local_348;
  void *local_344;
  int local_340;
  int local_33c;
  char local_338 [300];
  char local_20c [256];
  char local_10c [256];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d392f;
  local_c = ExceptionList;
  piVar6 = (int *)0x0;
  if (param_2 == (void *)0x0) {
    param_2 = param_1;
  }
  ExceptionList = &local_c;
  local_34c = (int *)OID__AllocObject(0x174,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0x982);
  local_4 = 0;
  if (local_34c != (int *)0x0) {
    piVar6 = (int *)CMesh__Init();
  }
  pvVar5 = (void *)piVar6[0x54];
  local_350 = piVar6[0x56];
  local_4 = 0xffffffff;
  piVar6[0x54] = 0;
  local_344 = pvVar5;
  CUnitAI__Unk_00423910((uint)param_1);
  CUnitAI__Unk_00423910((uint)param_2);
  CUnitAI__Unk_00423960(param_1,(int)local_338,300,1,(int)unaff_EDI);
  CUnitAI__Unk_00423960(param_1,(int)&local_340,4,1,(int)unaff_EDI);
  CUnitAI__Unk_00423960(param_1,(int)&local_33c,4,1,(int)unaff_EDI);
  if ((local_33c == 1) &&
     (bVar1 = CGame__Unk_00472570(&DAT_008a9a98,(int)local_338,unaff_EDI),
     CONCAT31(extraout_var,bVar1) == 0)) {
    sprintf(local_20c,s_Skipping_deserialisation_of_mesh_0062fd7c);
    DebugTrace(local_20c);
    CUnitAI__Unk_00423990(param_2);
    if (pvVar5 != (void *)0x0) {
      OID__FreeObject(pvVar5);
    }
    ExceptionList = local_c;
    return (int *)0x0;
  }
  CUnitAI__Unk_00423960(param_1,(int)&local_351,1,1,(int)unaff_EDI);
  if ((DAT_00704ae4 == '\0') && (local_338[0] != '\0')) {
    sprintf(local_10c,s_data_resources_meshes_m__s_aya_0062fd28);
    local_34c = (int *)OID__AllocObject(0x10,0x80,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0x9cc);
    local_4 = 1;
    if (local_34c == (int *)0x0) {
      param_2 = (void *)0x0;
    }
    else {
      param_2 = (void *)CChunker__Create();
    }
    local_4 = 0xffffffff;
    iVar2 = CUnitAI__Unk_004238c0(param_2,local_10c,(int)unaff_EDI);
    if (iVar2 == 0) {
      FatalError__ExitWithLocalizedPrefix_B(local_10c);
      if (param_2 != (void *)0x0) {
        CUnitAI__Unk_00423840((int)param_2);
        OID__FreeObject(param_2);
      }
      ExceptionList = local_c;
      return (int *)0x0;
    }
    DAT_00704ae4 = '\x01';
  }
  CUnitAI__Unk_00423910((uint)param_2);
  CUnitAI__Unk_00423960(param_2,(int)piVar6,0x174,1,(int)unaff_EDI);
  piVar6[0x55] = local_340;
  piVar6[0x56] = local_350;
  if (piVar6[5] < 1) {
    piVar6[6] = 0;
  }
  else {
    iVar2 = OID__AllocObject(piVar6[5] * 0x24,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0x9f7);
    piVar6[6] = iVar2;
  }
  iVar2 = piVar6[7];
  if (iVar2 < 1) {
    piVar6[8] = 0;
  }
  else {
    local_350 = OID__AllocObject(iVar2 * 0x150,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0x9fc);
    local_4 = 2;
    if (local_350 == 0) {
      iVar3 = 0;
    }
    else {
      iVar3 = local_350;
      if (-1 < iVar2 + -1) {
        pvVar5 = (void *)(local_350 + 0x10);
        do {
          vector_constructor_iterator_nothrow(pvVar5,0x10,3,&LAB_00402d20);
          pvVar5 = (void *)((int)pvVar5 + 0x150);
          iVar2 = iVar2 + -1;
        } while (iVar2 != 0);
        local_4 = 0xffffffff;
        piVar6[8] = local_350;
        goto LAB_004aae7d;
      }
    }
    local_4 = 0xffffffff;
    piVar6[8] = iVar3;
  }
LAB_004aae7d:
  DAT_00704ae8 = DAT_00704ae8 + piVar6[7] * 0x150;
  DebugTrace(s__dK_total_in_emitters_so_far_0062fd5c);
  iVar2 = piVar6[1];
  if (iVar2 < 1) {
    *piVar6 = 0;
  }
  else {
    local_34c = (int *)OID__AllocObject(iVar2 * 0x24 + 4,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,
                                        0xa05);
    local_4 = 3;
    if (local_34c == (int *)0x0) {
      local_4 = 0xffffffff;
      *piVar6 = 0;
    }
    else {
      piVar4 = local_34c + 1;
      *local_34c = iVar2;
      eh_vector_constructor_iterator
                (piVar4,0x24,iVar2,CInfluenceMap__Unk_004adf80,CExplosionInitThing__Unk_004adf90);
      local_4 = 0xffffffff;
      *piVar6 = (int)piVar4;
    }
  }
  iVar2 = 0;
  if (piVar6[3] < 1) {
    piVar6[4] = 0;
  }
  else {
    iVar3 = OID__AllocObject(piVar6[3] * 0xc,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0xa0a);
    piVar6[4] = iVar3;
  }
  CUnitAI__Unk_00423910((uint)param_2);
  CUnitAI__Unk_00423960(param_2,*piVar6,0x24,piVar6[1],(int)unaff_EDI);
  iVar3 = 0;
  if (0 < piVar6[1]) {
    do {
      CUnitAI__Unk_00423910((uint)param_2);
      *(undefined4 *)(*piVar6 + 0xc + iVar2) = 0;
      *(undefined4 *)(*piVar6 + 0x10 + iVar2) = 0;
      *(undefined4 *)(*piVar6 + 0x14 + iVar2) = 0;
      *(undefined4 *)(*piVar6 + 0x18 + iVar2) = 0;
      *(undefined4 *)(*piVar6 + 0x1c + iVar2) = 0;
      *(undefined4 *)(*piVar6 + 4 + iVar2) = 0;
      CMeshPart__SetVertexCount(*(undefined4 *)(*piVar6 + 8 + iVar2));
      CUnitAI__Unk_00423910((uint)param_2);
      CUnitAI__Unk_00423960
                (param_2,*(int *)(*piVar6 + iVar2 + 0xc),4,*(int *)(*piVar6 + iVar2 + 8),
                 (int)unaff_EDI);
      CUnitAI__Unk_00423960
                (param_2,*(int *)(*piVar6 + iVar2 + 0x10),4,*(int *)(*piVar6 + iVar2 + 8),
                 (int)unaff_EDI);
      CUnitAI__Unk_00423960
                (param_2,*(int *)(*piVar6 + iVar2 + 0x14),4,*(int *)(*piVar6 + iVar2 + 8),
                 (int)unaff_EDI);
      CUnitAI__Unk_00423960
                (param_2,*(int *)(*piVar6 + iVar2 + 0x18),4,*(int *)(*piVar6 + iVar2 + 8),
                 (int)unaff_EDI);
      CUnitAI__Unk_00423960
                (param_2,*(int *)(*piVar6 + iVar2 + 0x1c),4,*(int *)(*piVar6 + iVar2 + 8),
                 (int)unaff_EDI);
      CUnitAI__Unk_00423960(param_2,(int)local_20c,0x80,1,(int)unaff_EDI);
      piVar4 = CMesh__Unk_004aa410(local_20c);
      *(int **)(*piVar6 + iVar2) = piVar4;
      *(undefined4 *)(*piVar6 + 4 + iVar2) = 0;
      CMeshPart__Unk_004ae0d0((void *)(*piVar6 + iVar2));
      iVar3 = iVar3 + 1;
      iVar2 = iVar2 + 0x24;
    } while (iVar3 < piVar6[1]);
  }
  iVar2 = OID__AllocObject(piVar6[0x57] << 2,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0xa50);
  piVar6[0x58] = iVar2;
  iVar2 = 0;
  if (0 < piVar6[0x57]) {
    do {
      piVar4 = (int *)OID__AllocObject(0x13c,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0xa58);
      local_4 = 4;
      local_34c = piVar4;
      if (piVar4 == (int *)0x0) {
        piVar4 = (int *)0x0;
      }
      else {
        CMeshPart__Init();
      }
      iVar2 = iVar2 + 1;
      local_4 = 0xffffffff;
      *(int **)(piVar6[0x58] + -4 + iVar2 * 4) = piVar4;
    } while (iVar2 < piVar6[0x57]);
  }
  iVar2 = 0;
  if (0 < piVar6[0x57]) {
    do {
      CMeshPart__LoadFromStream(param_2,*(undefined4 *)(piVar6[0x58] + iVar2 * 4),piVar6);
      if ((local_351 == '\0') &&
         (pvVar5 = *(void **)(*(int *)(piVar6[0x58] + iVar2 * 4) + 0x100), pvVar5 != (void *)0x0)) {
        CInfluenceMap__Unk_004d3a00((int)pvVar5);
        OID__FreeObject(pvVar5);
        *(undefined4 *)(*(int *)(piVar6[0x58] + iVar2 * 4) + 0x100) = 0;
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < piVar6[0x57]);
  }
  if (0 < piVar6[3]) {
    CUnitAI__Unk_00423910((uint)param_2);
    CUnitAI__Unk_00423960(param_2,piVar6[4],0xc,piVar6[3],(int)unaff_EDI);
    iVar2 = 0;
    if (0 < piVar6[3]) {
      iVar3 = 0;
      do {
        if (*(int *)(iVar3 + piVar6[4]) != 0) {
          CUnitAI__Unk_00423910((uint)param_2);
          CUnitAI__Unk_00423960(param_2,(int)&local_350,4,1,(int)unaff_EDI);
          *(undefined4 *)(iVar3 + piVar6[4]) = *(undefined4 *)(piVar6[0x58] + local_350 * 4);
        }
        iVar2 = iVar2 + 1;
        iVar3 = iVar3 + 0xc;
      } while (iVar2 < piVar6[3]);
    }
  }
  if (0 < piVar6[5]) {
    CUnitAI__Unk_00423910((uint)param_2);
    CUnitAI__Unk_00423960(param_2,piVar6[6],0x24,piVar6[5],(int)unaff_EDI);
  }
  CUnitAI__Unk_00423910((uint)param_2);
  iVar2 = CMeshPart__LoadMaterial(param_2,local_344);
  piVar6[0x54] = iVar2;
  if (0 < piVar6[7]) {
    CUnitAI__Unk_00423910((uint)param_2);
    CUnitAI__Unk_00423960(param_2,(int)&local_348,4,1,(int)unaff_EDI);
    if (local_348 != 0x150) {
      DebugTrace(s_Size__d__sizeof__d_0062fd48);
    }
    iVar2 = 0;
    if (0 < piVar6[7]) {
      iVar3 = 0;
      do {
        CUnitAI__Unk_00423960(param_2,piVar6[8] + iVar3,local_348,1,(int)unaff_EDI);
        if (*(int *)(piVar6[8] + 0x40 + iVar3) != 0) {
          CUnitAI__Unk_00423960(param_2,(int)&local_34c,4,1,(int)unaff_EDI);
          *(undefined4 *)(piVar6[8] + 0x40 + iVar3) =
               *(undefined4 *)(piVar6[0x58] + (int)local_34c * 4);
        }
        iVar2 = iVar2 + 1;
        iVar3 = iVar3 + 0x150;
      } while (iVar2 < piVar6[7]);
    }
  }
  if (piVar6[2] != 0) {
    iVar2 = CMesh__Deserialize(param_1,param_2);
    piVar6[2] = iVar2;
    *(int *)(iVar2 + 0x170) = *(int *)(iVar2 + 0x170) + 1;
  }
  piVar6[0x5c] = 0;
  if (DAT_00704ae4 != '\0') {
    CUnitAI__Unk_00423900();
    if (param_2 != (void *)0x0) {
      CUnitAI__Unk_00423840((int)param_2);
      OID__FreeObject(param_2);
    }
    DAT_00704ae4 = '\0';
  }
  ExceptionList = local_c;
  return piVar6;
}
