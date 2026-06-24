/* address: 0x00590d25 */
/* name: CTexture__InitMemoryWriteStream */
/* signature: void __fastcall CTexture__InitMemoryWriteStream(void * param_1) */


void __fastcall CTexture__InitMemoryWriteStream(void *param_1)

{
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined ***)param_1 = &PTR_CDXTexture__QueryInterfaceByGuid_005ed3dc;
  *(undefined4 *)((int)param_1 + 4) = 1;
  return;
}
