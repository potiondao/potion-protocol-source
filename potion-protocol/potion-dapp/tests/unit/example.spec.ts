import { shallowMount } from "@vue/test-utils";
import Tag from "@/components/ui/Tag.vue";

describe("Tag.vue", () => {
  it("renders props.msg when passed", () => {
    const label = "new message";
    const wrapper = shallowMount(Tag, {
      propsData: { label },
    });
    expect(wrapper.text()).toMatch(label);
  });
});
