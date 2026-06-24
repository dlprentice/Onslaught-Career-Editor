/* address: 0x004aa500 */
/* name: CRTMesh__GetMaterialNameAndIdByIndex */
/* signature: void __thiscall CRTMesh__GetMaterialNameAndIdByIndex(void * this, int material_index, void * out_name, void * out_material_id, void * unused_ctx) */


void __thiscall
CRTMesh__GetMaterialNameAndIdByIndex
          (void *this,int material_index,void *out_name,void *out_material_id,void *unused_ctx)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  char *pcVar5;
  char *pcVar6;

  iVar2 = *(int *)((int)this + 0x1c);
  if (iVar2 <= material_index) {
    do {
      this = *(void **)((int)this + 8);
      if (this == (void *)0x0) {
        uVar3 = 0xffffffff;
        pcVar5 = &DAT_00662b2c;
        goto code_r0x004aa575;
      }
      material_index = material_index - iVar2;
      iVar2 = *(int *)((int)this + 0x1c);
    } while (iVar2 <= material_index);
  }
  uVar3 = 0xffffffff;
  pcVar5 = (char *)(*(int *)((int)this + 0x20) + 0x4c + material_index * 0x150);
  do {
    pcVar6 = pcVar5;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar6 = pcVar5 + 1;
    cVar1 = *pcVar5;
    pcVar5 = pcVar6;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  pcVar5 = pcVar6 + -uVar3;
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)out_name = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    out_name = (char *)((int)out_name + 4);
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *(char *)out_name = *pcVar5;
    pcVar5 = pcVar5 + 1;
    out_name = (char *)((int)out_name + 1);
  }
  *(undefined4 *)out_material_id =
       *(undefined4 *)(*(int *)((int)this + 0x20) + 0x14c + material_index * 0x150);
  return;
  while( true ) {
    uVar3 = uVar3 - 1;
    pcVar6 = pcVar5 + 1;
    cVar1 = *pcVar5;
    pcVar5 = pcVar6;
    if (cVar1 == '\0') break;
code_r0x004aa575:
    pcVar6 = pcVar5;
    if (uVar3 == 0) break;
  }
  uVar3 = ~uVar3;
  pcVar5 = pcVar6 + -uVar3;
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)out_name = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    out_name = (char *)((int)out_name + 4);
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *(char *)out_name = *pcVar5;
    pcVar5 = pcVar5 + 1;
    out_name = (char *)((int)out_name + 1);
  }
  *(undefined4 *)out_material_id = 0xffffffff;
  return;
}
