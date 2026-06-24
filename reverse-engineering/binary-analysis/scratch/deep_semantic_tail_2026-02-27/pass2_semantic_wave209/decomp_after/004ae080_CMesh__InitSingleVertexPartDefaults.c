/* address: 0x004ae080 */
/* name: CMesh__InitSingleVertexPartDefaults */
/* signature: void __fastcall CMesh__InitSingleVertexPartDefaults(void * param_1) */


void __fastcall CMesh__InitSingleVertexPartDefaults(void *param_1)

{
  *(undefined4 *)param_1 = 0;
  CMeshPart__SetVertexCount(1);
  **(undefined4 **)((int)param_1 + 0x10) = 0;
  **(undefined4 **)((int)param_1 + 0x14) = 0;
  **(undefined4 **)((int)param_1 + 0x18) = 0x3f800000;
  **(undefined4 **)((int)param_1 + 0x1c) = 0x3f800000;
  **(undefined4 **)((int)param_1 + 0xc) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 0x20) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 4) = 0;
  return;
}
