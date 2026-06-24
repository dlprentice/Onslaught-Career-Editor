/* address: 0x00578758 */
/* name: CDXTexture__Unk_00578758 */
/* signature: void __stdcall CDXTexture__Unk_00578758(void * param_1, void * param_2, void * param_3) */


void CDXTexture__Unk_00578758(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;

  fVar1 = *(float *)((int)param_3 + 4);
  fVar2 = *(float *)param_2;
  fVar3 = *(float *)((int)param_3 + 0x14);
  fVar4 = *(float *)((int)param_2 + 4);
  *(float *)param_1 =
       *(float *)param_2 * *(float *)param_3 +
       *(float *)((int)param_3 + 0x10) * *(float *)((int)param_2 + 4);
  *(float *)((int)param_1 + 4) = fVar3 * fVar4 + fVar1 * fVar2;
  return;
}
